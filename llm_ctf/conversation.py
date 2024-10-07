import json
import time
from datetime import datetime
import subprocess
import os
import traceback as tb
import openai
import anthropic
import getpass

from pathlib import Path
from .environment import CTFEnvironment
from .ctflogging import status
from .backends import Backend
from .formatters import Formatter
from .prompts.prompts import PromptManager
from .tools.manager import TOOLSETS, GiveUpException, Tool, CommandExec

SCRIPT_DIR = Path(__file__).parent.parent.resolve()

class CTFConversation:
    def __init__(self, env : CTFEnvironment, args : dict, config=None):
        self.args = args
        self.env = env
        self.chal = self.env.challenge
        self.volume = self.env.tmpdir
        self.available_functions : dict[str,Tool] = {}
        for tool in TOOLSETS.get(self.chal.category, TOOLSETS['default']):
            tool_instance = tool(self.env)
            self.available_functions[tool_instance.name] = tool_instance
        self.rounds = 0
        self.start_time = datetime.now()
        self.finish_reason = "unknown"
        self.config = config
        self.prompt_manager = PromptManager(args.prompt_set, config=config)
        self.backend = Backend.from_name(args.backend)(
            self.prompt_manager.system_message(self.chal),
            self.prompt_manager.hints_message(),
            self.available_functions,
            self.args,
        )
        self.cost = 0
        self.times = {
            'model_time': 0.0,
            'tool_time': 0.0,
        }

    def __enter__(self):
        for tool in self.available_functions.values():
            tool.setup()
        self.backend.setup()
        return self
    

    def check_flag(self, resp : str):
        # Check if the flag is in the response; also check version with
        # escaped underscores because the model is writing Markdown and
        # sometimes gets over-eager about escaping things. Would be nice
        # to properly unescape the response with a Markdown parser but
        # apparently that's more difficult than it should be.
        unescaped_resp = resp.replace('\\_','_')
        if self.chal.flag in resp or self.chal.flag in unescaped_resp:
            status.print(
                f"\n[red bold]Correct flag found in the output:[/red bold] [green]{self.chal.flag}[/green]",
                markup=True)
            self.solved = True
            return True
        else:
            return False

    def run_conversation_step(self, message: str):
        status.user_message(message)
        # Step 1: send the initial message to the model
        st = time.time()
        content, tool_calls, cost = self.backend.send(message)
        self.times['model_time'] += time.time() - st
        self.cost += cost
        if not content:
            if tool_calls:
                status.assistant_message("🤔 ...thinking... 🤔")
            else:
                status.assistant_message("[ no response ]")
        else:
            status.assistant_message(content)
        yield content

        # Check if the conversation has gone on too long
        self.rounds += 1
        if self.rounds > self.args.max_rounds:
            status.print(
                f"[red bold]Challenge is unsolved after {self.args.max_rounds} rounds; exiting[/red bold]",
                markup=True
            )
            self.finish_reason = "max_rounds"
            return
        if self.cost > self.args.max_cost:
            status.print(
                f"[red bold]Challenge is unsolved after {self.args.max_cost} dollars of cost; exiting[/red bold]",
                markup=True
            )
            self.finish_reason = "max_cost"
            return

        # Step 2: if the model wants to call functions, call them and send back the results,
        # repeating until the model doesn't want to call any more functions
        while tool_calls:
            st = time.time()
            content, tool_calls, cost = self.backend.run_tools()
            self.times['tool_time'] += time.time() - st
            # Send the tool results back to the model
            st = time.time()
            self.times['model_time'] += time.time() - st
            self.cost += cost
            if not content:
                if tool_calls:
                    status.assistant_message("🤔 ...thinking... 🤔")
                else:
                    status.assistant_message("[ no response ]")
            else:
                status.assistant_message(content)

            # Return control to the caller so they can check the response for the flag
            yield content

            # Check if the conversation has gone on too long
            self.rounds += 1
            if self.rounds > self.args.max_rounds:
                status.print(
                    f"[red bold]Challenge is unsolved after {self.args.max_rounds} rounds; exiting[/red bold]",
                    markup=True
                )
                return
            if self.cost > self.args.max_cost:
                status.print(
                    f"[red bold]Challenge is unsolved after {self.args.max_cost} dollars of cost; exiting[/red bold]",
                    markup=True
                )
                self.finish_reason = "max_cost"
                return

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = datetime.now()

        # Tear down the tools first so they can clean up
        for tool in self.available_functions.values():
            tool.teardown(exc_type, exc_value, traceback)

        # If there was an exception, convert it to a dict so we can serialize it
        if exc_type is None:
            exception_info = None
        else:
            # Extracting traceback details
            tb_list = tb.format_tb(traceback)
            tb_string = ''.join(tb_list)

            # Constructing the JSON object
            exception_info = {
                "exception_type": str(exc_type.__name__),
                "exception_message": str(exc_value),
                "traceback": tb_string
            }
            self.finish_reason = "exception"

        # Save the conversation to a file
        if self.args.logdir:
            logdir = Path(self.args.logdir).resolve()
            logfile = logdir / f"{self.chal.canonical_name}.json"
        else:
            logdir = SCRIPT_DIR / f"logs/{getpass.getuser()}/{self.args.experiment_name}_{self.args.database}_{self.args.index}"
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            logfile = logdir / f"{self.chal.canonical_name}.json"
        logdir.mkdir(parents=True, exist_ok=True)
        logfile.write_text(json.dumps(
            {
                "args": vars(self.args),
                "messages": self.backend.get_timestamped_messages(),
                "challenge": self.chal.challenge,
                "solved": self.chal.solved,
                "rounds": self.rounds,
                "debug_log": status.debug_log,
                "challenge_server_output": self.chal.challenge_server_output,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "runtime_seconds": (self.end_time - self.start_time).total_seconds(),
                "times": self.times,
                "exception_info": exception_info,
                "finish_reason": self.finish_reason,
            },
            indent=4
        ))
        status.print(f"Conversation saved to {logfile}")

    def run(self):
        next_msg = self.prompt_manager.initial_message(self.chal)
        # # Add hints message to initial
        # hints_msg = self.prompt_manager.hints_message(self.chal, hints=self.args.hints)
        # if len(hints_msg) != 0:
        #     next_msg += "\n\n" + hints_msg
        # elif len(self.args.hints) != 0:
        #     status.debug_message(f"hints {self.args.hints} not found")

        try:
            while True:
                for resp in self.run_conversation_step(next_msg):
                    if self.chal.solved or (resp and self.check_flag(resp)):
                        status.print(
                            "[red bold]Challenge solved by our robot overlords![/red bold]",
                            markup=True
                        )
                        self.finish_reason = "solved"
                        return 0
                    else:
                        # No flag in the response, just keep going
                        pass
                # Check if we returned from the conversation loop because we hit the max rounds
                if self.rounds > self.args.max_rounds:
                    self.finish_reason = "max_rounds"
                    return 1
                # Otherwise, we returned because the model didn't respond with anything; prompt
                # it to keep going.
                next_msg = "Please proceed to the next step using your best judgment."
        except GiveUpException:
            status.print(
                "[red bold]The LLM decided to give up! NGMI.[/red bold]",
                markup=True
            )
            self.convo.finish_reason = "give_up"
            return 0
        except KeyboardInterrupt:
            status.print(
                "[red bold]Interrupted by user[/red bold]",
                markup=True
            )
            self.convo.finish_reason = "user_cancel"
            if self.args.debug:
                # Print traceback
                tb.print_exc()
            return 0
        except (openai.RateLimitError, anthropic.RateLimitError):
            status.print("[red bold]Rate limit reached![/red bold]", markup=True)
            self.finish_reason = "rate_limit"
            return 0
        except openai.BadRequestError as e:
            msg = str(e)
            if "'code': 'context_length_exceeded'" in msg or "'code': 'string_above_max_length'" in msg:
                status.print("[red bold]Context length exceeded![/red bold]", markup=True)
                self.finish_reason = "context_length"
                return 0
            else:
                # Some other error, re-raise
                raise