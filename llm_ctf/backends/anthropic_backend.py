from argparse import Namespace
import os
from typing import List, Optional, Tuple, Union

from .backend import Backend
from .openai_backend import make_call_result
from ..utils import timestamp
from ..toolset.tools import Tool, ToolCall, ToolResult
from ..formatters.formatter import Formatter
from ..ctflogging import status

from anthropic import Anthropic
from anthropic.types import Message as AnthropicMessage

API_KEY_PATH = "~/.config/anthropic/api_key"

class AnthropicBackend(Backend):
    """Anthropic backend.

    It follows the same pattern as the Mixtral backend, with custom
    formatters and demonstration messages to help the model.
    """
    NAME = 'anthropic'
    MODELS = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
    ]

    def __init__(self, system_message : str, tools : List[Tool], args : Namespace):
        self.tools = {tool.name: tool for tool in tools}
        self.args = args
        self.formatter : Formatter = Formatter.from_name(args.formatter)(tools, args.prompt_set)
        self.system_message = system_message

        if args.api_key is None:
            if "ANTHROPIC_API_KEY" in os.environ:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            elif os.path.exists(os.path.expanduser(API_KEY_PATH)):
                api_key = open(os.path.expanduser(API_KEY_PATH), "r").read().strip()
            else:
                raise ValueError(f"No Anthropic API key provided and none found in ANTHROPIC_API_KEY or {API_KEY_PATH}")
        if args.model:
            if args.model not in MODELS:
                raise ValueError(f"Invalid model {args.model}. Must be one of {MODELS}")
            self.model = args.model
        else:
            self.model = MODELS[0]
            # Update the args object so that the model name will be included in the logs
            args.model = self.model

        os.environ["ANTHROPIC_API_KEY"] = api_key
        self.client = Anthropic(api_key=api_key)

        self.messages = []
        self.outgoing_messages = []

    @classmethod
    def get_models(cls):
        return MODELS

    def setup(self):
        self.system_message += '\n\n' + self.formatter.tool_use_prompt()

        for m in self.get_initial_messages():
            self.append(m)

    def get_initial_messages(self):
        # Create demonstration messages
        run_command = self.tools['run_command']
        uname_whoami_msg = self.formatter.tool_call_prompt([
            run_command.make_call(command="uname -a"),
            run_command.make_call(command="whoami"),
        ])
        uname_whoami_calls = self.formatter.extract_tool_calls(uname_whoami_msg)
        uname_whoami_result_message = self.tool_result_message(self._run_tools_internal(uname_whoami_calls))
        cat_call_msg = self.formatter.tool_call_prompt([
            run_command.make_call(command="cat /etc/os-release"),
        ])
        cat_calls = self.formatter.extract_tool_calls(cat_call_msg)
        cat_result_message = self.tool_result_message(self._run_tools_internal(cat_calls))

        # Include an example of a tool call
        demonstration_messages = [
            {"role": "user", "content": "First let's make sure you know how to use tools. What are the current user, CPU architecture, and Linux distribution in your environment?"},
            {"role": "assistant", "content": uname_whoami_msg}
        ] + [uname_whoami_result_message] + [
            {"role": "assistant", "content": cat_call_msg}
        ] + [cat_result_message] + [
            {"role": "assistant", "content": "The current user is `ctfplayer`, the CPU architecture is `x86_64`, and the Linux distribution is `Ubuntu 22.04.3 LTS`."}
        ]

        return demonstration_messages

    def _run_tools_internal(self, tool_calls : List[ToolCall]) -> List[ToolResult]:
        tool_results = []
        for tool_call in tool_calls:
            function_name = tool_call.name

            # Tool lookup
            tool = self.tools.get(function_name)
            if not tool:
                if function_name == "[not provided]":
                    msg = "No tool name provided"
                else:
                    msg = f"Unknown tool {function_name}"
                self.messages.append(tool_call.error(msg))
                continue

            # Parameter parsing
            try:
                parsed_tc = self.formatter.extract_params(tool, tool_call)
                # Upgrade the tool call to a parsed tool call
                tool_call.create_parsed(parsed_tc)
            except ValueError as e:
                status.debug_message(f"Error extracting parameters for {function_name}: {e}")
                tool_results.append(
                    tool_call.error(f"{type(e).__name__} extracting parameters for {function_name}: {e}")
                )
                continue

            # Tool execution
            status.debug_message(f"Calling {parsed_tc}")
            # Don't catch exceptions here; let them propagate up since it means something
            # went wrong in our tool code (and we want GiveUpExceptions to bubble up)
            result = tool.run(parsed_tc)
            status.debug_message(f"=> {result.result}", truncate=True)
            tool_results.append(result)
        return tool_results

    def user_message(self, content : str):
        return {"role": "user", "content": content}

    def tool_result_message(self, tool_results : List[ToolResult]):
        return self.user_message(self.formatter.format_results(tool_results))

    def response_to_message(self, response : AnthropicMessage) -> dict:
        return {
            "role": response.role,
            "content": response.content[0].text,
        }

    def _call_model(self):
        start_seqs, stop_seqs = self.formatter.get_delimiters()
        response = self.client.messages.create(
            model=self.model,
            messages=self.outgoing_messages,
            temperature=1,
            max_tokens=1024,
            stop_sequences=stop_seqs,
            system=self.system_message,
        )
        if response.stop_reason == "stop_sequence":
            response.content[0].text += response.stop_sequence

        if any(s in response.content[0].text for s in start_seqs):
            has_tool_calls = True
        else:
            has_tool_calls = False
        status.debug_message(f"Response:\n{response.content[0].text}", truncate=False)
        content = self.formatter.extract_content(response.content[0].text)
        return response, content, has_tool_calls

    # Anthropic doesn't accept their own response object as a message, so we need to convert it.
    # We keep the original around for logging purposes.
    def append(self, message : Union[dict,AnthropicMessage,List[ToolResult]]):
        if isinstance(message, dict):
            conv_message = message
        elif isinstance(message, list):
            conv_message = self.tool_result_message(message)
        elif isinstance(message, AnthropicMessage):
            conv_message = self.response_to_message(message)
        else:
            raise ValueError(f"Unknown message type: {type(message)}")
        self.outgoing_messages.append(conv_message)
        self.messages.append(message)

    def run_tools(self):
        try:
            tool_calls = self.formatter.extract_tool_calls(self.messages[-1].content[0].text)
        except Exception as e:
            status.debug_message(f"Error extracting tool calls: {e}")
            tool_calls = []
        tool_results = self._run_tools_internal(tool_calls)
        self.append(tool_results)
        response, content, has_tool_calls = self._call_model()
        self.append(response)
        return content, has_tool_calls

    def send(self, message : str) -> Tuple[Optional[str],bool]:
        self.append(self.user_message(message))
        response, content, has_tool_calls = self._call_model()
        self.append(response)
        return content, has_tool_calls

    def convert_message(self, m):
        if isinstance(m, dict):
            return m
        else:
            return m.model_dump()
