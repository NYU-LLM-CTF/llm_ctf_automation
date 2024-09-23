<<<<<<< HEAD
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
from nyuctf.challenge import CTFChallenge

from .ctflogging import status
from .backends import Backend
from .formatters import Formatter
from .prompts.prompts import PromptManager
from .tools.manager import TOOLSETS, GiveUpException, Tool, CommandExec
from .environment import CTFEnvironment

class CTFConversation:
    def __init__(self, environment: CTFEnvironment, challenge: CTFChallenge, prompt_manager: PromptManager, backend: Backend, max_rounds:int=30, max_cost:float=1.0):
        self.challenge = challenge
        self.environment = environment
        self.prompt_manager = prompt_manager
        self.backend = backend

        self.available_functions : dict[str,Tool] = {}

        self.max_rounds = max_rounds
        self.max_cost = max_cost
        self.config = config

        self.solved = False
        self.rounds = 0
        self.cost = 0
        self.finish_reason = "unknown"
        self.model_time = 0
        self.tool_time = 0

    def __enter__(self):
        self.backend.setup()
        self.start_time = datetime.now()
        return self

    def run(self):
        while not self.solved and self.rounds <= self.max_rounds and self.cost <= self.max_cost:
            resp, tool_call, cost = self.run_conversation_step(next_msg)

        if self.rounds > self.max_rounds:
            status.print(f"[red bold]Challenge is unsolved after {self.max_rounds} rounds; exiting[/red bold]", markup=True)
            self.finish_reason = "max_rounds"
        elif self.cost > self.max_cost:
            status.print(f"[red bold]Challenge is unsolved after {self.max_cost} dollars of cost; exiting[/red bold]", markup=True)
            self.finish_reason = "max_cost"

        # TODO return here


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
            # TODO Shouldn't be handled by exception
            status.print(
                "[red bold]The LLM decided to give up! NGMI.[/red bold]",
                markup=True
            )
            convo.finish_reason = "give_up"
        except KeyboardInterrupt:
            status.print(
                "[red bold]Interrupted by user[/red bold]",
                markup=True
            )
            convo.finish_reason = "user_cancel"
        # TODO Normalize the ratelimiterrors
        except (openai.RateLimitError, anthropic.RateLimitError):
            status.print("[red bold]Rate limit reached![/red bold]", markup=True)
            convo.finish_reason = "rate_limit"
        except openai.BadRequestError as e:
            msg = str(e)
            if "'code': 'context_length_exceeded'" in msg or "'code': 'string_above_max_length'" in msg:
                status.print("[red bold]Context length exceeded![/red bold]", markup=True)
                convo.finish_reason = "context_length"
            else:
                # Some other error, re-raise
                raise

    def run_conversation_step(self, message: str):
        status.user_message(message)
        status.assistant_message("🤔 ...thinking... 🤔")

        # Prompt the model to produce a response and tool_calls
        st = time.time()
        content, tool_calls, cost = self.backend.send(message)
        self.times['model_time'] += time.time() - st
        self.rounds += 1
        self.cost += cost

        if content:
            status.assistant_message(content)
        else:
            status.assistant_message("[ no response ]")

        # Run tool calls
        if tool_calls:
            st = time.time()
            self.environment.run_tools(tool_calls)
            self.times['tool_time'] += time.time() - st

        # TODO process tool results

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = datetime.now()

        # Save the conversation to a file
        logfile = logdir / f"{self.chal.canonical_name}.json"
        logfile.write_text(json.dumps(
            {
                "args": vars(self.args),
                "messages": self.backend.get_timestamped_messages(),
                "challenge": self.chal.challenge,
                "solved": self.solved,
                "rounds": self.rounds,
                "cost": self.cost,
                "debug_log": status.debug_log,
                # "challenge_server_output": self.chal.challenge_server_output,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "runtime": {
                    "total": (self.end_time - self.start_time).total_seconds(),
                    "tools": self.tool_time,
                    "model": self.model_time
                },
                # "exception_info": exception_info,
                "finish_reason": self.finish_reason,
            },
            indent=4
        ))
        status.print(f"Conversation saved to {logfilename}")
