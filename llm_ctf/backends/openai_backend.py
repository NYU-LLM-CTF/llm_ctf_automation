#!/usr/bin/env python3

from argparse import Namespace
import json
from openai import OpenAI
import os
from typing import List, Optional, Tuple
from .backend import Backend
from ..tools import Tool, ToolCall, ToolResult
from ..ctflogging import status
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall as OAIToolCall
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

MODELS = [
    "gpt-4-1106-preview",
    "gpt-4-0125-preview",
    "gpt-3.5-turbo-1106",
]
API_KEY_PATH = "~/.openai/api_key"

def get_tool_calls(otc_calls : List[OAIToolCall]) -> List[ToolCall]:
    return [ToolCall.make(otc.function.name, otc.id, otc.function.arguments) for otc in otc_calls]

def make_call_result(res : ToolResult):
    return dict(
        name=res.name,
        role="tool",
        content=json.dumps(res.result),
        tool_call_id=res.id,
    )

class OpenAIBackend(Backend):
    NAME = 'openai'

    def __init__(self, system_message: str, tools : List[Tool], args : Namespace):
        if args.api_key is None:
            if "OPENAI_API_KEY" in os.environ:
                api_key = os.environ["OPENAI_API_KEY"]
            elif os.path.exists(os.path.expanduser(API_KEY_PATH)):
                api_key = open(os.path.expanduser(API_KEY_PATH), "r").read().strip()
            else:
                raise ValueError(f"No OpenAI API key provided and none found in OPENAI_API_KEY or {API_KEY_PATH}")
        self.client = OpenAI(api_key=api_key)
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [ChatCompletionToolParam(**tool.schema) for tool in tools]
        if args.model:
            if args.model not in MODELS:
                raise ValueError(f"Invalid model {args.model}. Must be one of {MODELS}")
            self.model = args.model
        else:
            self.model = MODELS[0]
            # Update the args object so that the model name will be included in the logs
            args.model = self.model

        self.system_message = system_message
        self.messages = self.get_initial_messages(self.system_message)

    def get_initial_messages(self, system_message : str):
        return [
            self._system_message(system_message),
        ]

    @classmethod
    def get_models(cls):
        return MODELS

    def _call_model(self) -> ChatCompletionMessage:
        return self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool_schemas,
            tool_choice="auto",
        ).choices[0].message

    def _message(self, content : str, role : str) -> dict[str,str]:
        return {
            "role": role,
            "content": content,
        }

    def _user_message(self, content : str) -> dict[str,str]:
        return self._message(content, "user")

    def _system_message(self, content : str) -> dict[str,str]:
        return self._message(content, "system")

    def send(self, message : str) -> Tuple[Optional[str],bool]:
        self.messages.append(self._user_message(message))
        response = self._call_model()
        self.messages.append(response)
        return response.content, bool(response.tool_calls)

    def run_tools(self) -> Tuple[Optional[str],bool]:
        tool_calls = get_tool_calls(self.messages[-1].tool_calls)
        tool_results = []
        for tool_call in tool_calls:
            # Tool lookup
            function_name = tool_call.name
            tool = self.tools.get(function_name)
            if not tool:
                tool_res = tool_call.error(f"Unknown tool {function_name}")
                tool_results.append(make_call_result(tool_res))
                continue

            # Parameter parsing
            try:
                arguments = self.extract_parameters(tool, tool_call)
            except json.JSONDecodeError as e:
                status.debug_message(f"Error decoding arguments for {function_name}: {e}")
                status.debug_message(f"Arguments: {tool_call.function.arguments}")
                tool_res = tool_call.error(f"{type(e).__name__} decoding arguments for {function_name}: {e}")
                tool_results.append(make_call_result(tool_res))
                continue
            except ValueError as e:
                status.debug_message(f"Error extracting parameters for {function_name}: {e}")
                tool_res = tool_call.error(
                    f"{type(e).__name__} extracting parameters for {function_name}: {e}"
                )
                tool_results.append(make_call_result(tool_res))
                continue

            # Tool execution
            status.debug_message(f"Calling {arguments}")
            tool_res_plain = tool.run(arguments)
            status.debug_message(f"=> {tool_res_plain.result}", truncate=True)
            try:
                tool_res = make_call_result(tool_res_plain)
            except TypeError as e:
                status.debug_message(f"Error encoding results from {function_name}: {e}")
                tool_res = make_call_result(tool_call.error(
                    f"{type(e).__name__} running {function_name}: {e}"
                ))
            except Exception as e:
                status.debug_message(f"Error running {function_name}: {e}")
                tool_res = make_call_result(tool_call.error(
                    f"{type(e).__name__} running {function_name}: {e}"
                ))
            tool_results.append(tool_res)
        self.messages += tool_results
        response = self._call_model()
        self.messages.append(response)
        return response.content, bool(response.tool_calls)

    def get_message_log(self) -> List[dict]:
        return [ m if isinstance(m,dict) else m.model_dump() for m in self.messages]

    @staticmethod
    def extract_parameters(tool : Tool, tc : ToolCall) -> ToolCall:
        """Extract and validate parameters from a tool call args"""
        parsed = json.loads(tc.function.arguments)
        parsed_arguments = {}
        for param_name in tool.parameters['properties']:
            if param_name in tool.parameters['required'] and param_name not in parsed:
                raise ValueError(f"Missing required parameter {param_name}")
            parsed_arguments[param_name] = parsed.get(param_name)
        for param_name,value in parsed.items():
            if param_name not in tool.parameters['properties']:
                status.debug_message(f"WARNING: Model used unknown parameter {param_name}={value} in call to {tool.name}")
        parsed_tc = tc.clone()
        parsed_tc.function.parsed_arguments = parsed_arguments
        return parsed_tc
