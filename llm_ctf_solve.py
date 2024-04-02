from datetime import datetime
import time
from openai import OpenAI
import json, os
import argparse
import shutil
from pathlib import Path
from llm_ctf.ctflogging import status
from llm_ctf.backends import Backend
from llm_ctf.formatters import Formatter
from llm_ctf.prompts.prompts import PromptManager
from llm_ctf.tools import TOOLSETS, GiveUpException
from llm_ctf.challenge import CTFChallenge
import traceback as tb

SCRIPT_DIR = Path(__file__).parent.resolve()

class CTFConversation:
    def __init__(self, challenge : CTFChallenge, args : argparse.Namespace):
        self.args = args
        self.chal = challenge
        self.volume = self.chal.tmpdir
        self.available_functions = {}
        for tool in TOOLSETS.get(self.chal.category, TOOLSETS['default']):
            tool_instance = tool(self.chal)
            self.available_functions[tool_instance.name] = tool_instance
        self.rounds = 0
        self.start_time = datetime.now()
        self.finish_reason = "unknown"
        self.prompt_manager = PromptManager(args.prompt_set)
        self.backend = Backend.from_name(args.backend)(
            self.prompt_manager.system_message(),
            self.available_functions.values(),
            self.args,
        )
        self.times = {
            'model_time': 0.0,
            'tool_time': 0.0,
        }

    def __enter__(self):
        for tool in self.available_functions.values():
            tool.setup()
        self.backend.setup()
        status.system_message(self.prompt_manager.system_message())
        return self

    def run_conversation_step(self, message: str):
        status.user_message(message)
        # Step 1: send the initial message to the model
        st = time.time()
        content, tool_calls = self.backend.send(message)
        self.times['model_time'] += time.time() - st
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

        # Step 2: if the model wants to call functions, call them and send back the results,
        # repeating until the model doesn't want to call any more functions
        while tool_calls:
            st = time.time()
            content, tool_calls = self.backend.run_tools()
            self.times['tool_time'] += time.time() - st
            # Send the tool results back to the model
            st = time.time()
            self.times['model_time'] += time.time() - st
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

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = datetime.now()

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
        if self.args.logfile:
            logfilename = Path(self.args.logfile)
            logdir = logfilename.parent
        else:
            logdir = SCRIPT_DIR / f"logs/{self.chal.category}/{self.chal.chaldir.name}"
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            logfilename = logdir / f"conversation.{timestamp}.json"
        logdir.mkdir(parents=True, exist_ok=True)
        logfilename.write_text(json.dumps(
            {
                "args": vars(self.args),
                "messages": self.backend.get_timestamped_messages(),
                "challenge": self.chal.challenge,
                "solved": self.chal.solved,
                "rounds": self.rounds,
                "debug_log": status.debug_log,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "runtime_seconds": (self.end_time - self.start_time).total_seconds(),
                "times": self.times,
                "exception_info": exception_info,
                "finish_reason": self.finish_reason,
            },
            indent=4
        ))
        status.print(f"Conversation saved to {logfilename}")

        for tool in self.available_functions.values():
            tool.teardown(exc_type, exc_value, traceback)

def main():
    parser = argparse.ArgumentParser(
        description="Use an LLM to solve a CTF challenge",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    model_list = []
    for b in Backend.registry.values():
        model_list += b.get_models()
    model_list = list(set(model_list))

    parser.add_argument("challenge_json", help="path to the JSON file describing the challenge")
    parser.add_argument("-q", "--quiet", action="store_true", help="don't print messages to the console")
    parser.add_argument("-d", "--debug", action="store_true", help="print debug messages")
    parser.add_argument("-M", "--model", help="the model to use (default is backend-specific)", choices=model_list)
    parser.add_argument("-C", "--container-image", default="ctfenv", help="the Docker image to use for the CTF environment")
    parser.add_argument("-N", "--network", default="ctfnet", help="the Docker network to use for the CTF environment")
    parser.add_argument("-m", "--max-rounds", type=int, default=100, help="maximum number of rounds to run")
    parser.add_argument("-L", "--logfile", default=None, help="log file to write to")
    parser.add_argument("--api-key", default=None, help="API key to use when calling the model")
    parser.add_argument("--api-endpoint", default=None, help="API endpoint URL to use when calling the model")
    parser.add_argument("--backend", default="openai", choices=Backend.registry.keys(), help="model backend to use")
    parser.add_argument("--formatter", default="xml", choices=Formatter.registry.keys(), help="prompt formatter to use")
    parser.add_argument("--prompt-set", default="default", help="set of prompts to use")
    parser.add_argument("--disable-docker", default=False, action="store_true", help="disable Docker usage (for debugging)")
    parser.add_argument("--disable-markdown", default=False, action="store_true", help="don't render Markdown formatting in messages")
    args = parser.parse_args()
    status.set(quiet=args.quiet, debug=args.debug, disable_markdown=args.disable_markdown)
    challenge_json = Path(args.challenge_json).resolve()
    prompt_manager = PromptManager(args.prompt_set)
    with CTFChallenge(challenge_json, args) as chal, \
         CTFConversation(chal, args) as convo:
        next_msg = prompt_manager.initial_message(chal)
        try:
            while True:
                for resp in convo.run_conversation_step(next_msg):
                    if chal.solved or (resp and chal.check_flag(resp)):
                        status.print(
                            "[red bold]Challenge solved by our robot overlords![/red bold]",
                            markup=True
                        )
                        convo.finish_reason = "solved"
                        return 0
                    else:
                        # No flag in the response, just keep going
                        pass
                # Check if we returned from the conversation loop because we hit the max rounds
                if convo.rounds > args.max_rounds:
                    convo.finish_reason = "max_rounds"
                    return 1
                # Otherwise, we returned because the model didn't respond with anything; prompt
                # it to keep going.
                next_msg = "Please proceed to the next step using your best judgment."
        except GiveUpException:
            status.print(
                "[red bold]The LLM decided to give up! NGMI.[/red bold]",
                markup=True
            )
            convo.finish_reason = "give_up"
            return 0
        except KeyboardInterrupt:
            status.print(
                "[red bold]Interrupted by user[/red bold]",
                markup=True
            )
            convo.finish_reason = "user_cancel"
            if args.debug:
                # Print traceback
                tb.print_exc()
            return 0

if __name__ == "__main__":
    exit(main())
