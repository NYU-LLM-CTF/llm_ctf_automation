#!/usr/bin/env python3

from argparse import Namespace
import json
from openai import OpenAI
import os
from typing import List, Optional, Tuple
import tiktoken

from .backend import Backend, ToolCall
from ..tools.manager import Tool
from ..ctflogging import status
from openai import RateLimitError
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall as OAIToolCall
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from .utils import KEYS, MODEL_INFO

import backoff  # for exponential backoff

API_KEY_PATH = "~/.openai/api_key"

def get_tool_calls(otc_calls : List[OAIToolCall]) -> List[ToolCall]:
    return [ToolCall.create_unparsed(otc.function.name, otc.id, otc.function.arguments) for otc in otc_calls]

def count_token(message: str, model: str):
    if not message:
        return 0
    enc = tiktoken.encoding_for_model(model_name=model)
    num_tokens = len(enc.encode(message))
    return num_tokens

class OpenAIBackend(Backend):
    NAME = 'openai'
    MODELS = list(MODEL_INFO[NAME].keys())

    def __init__(self, system_message : str, tools: dict[str,Tool], args : Namespace):
        self.args = args
        if args.api_key is None:
            if "OPENAI_API_KEY" in KEYS:
                api_key = KEYS["OPENAI_API_KEY"].strip()
            if "OPENAI_API_KEY" in os.environ:
                api_key = os.environ["OPENAI_API_KEY"]
            elif os.path.exists(os.path.expanduser(API_KEY_PATH)):
                api_key = open(os.path.expanduser(API_KEY_PATH), "r").read().strip()
            else:
                raise ValueError(f"No OpenAI API key provided and none found in OPENAI_API_KEY or {API_KEY_PATH}")
        self.client = OpenAI(api_key=api_key)
        self.tools = tools
        self.tool_schemas = [ChatCompletionToolParam(**tool.schema) for tool in tools.values()]
        if args.model:
            if args.model not in self.MODELS:
                raise ValueError(f"Invalid model {args.model}. Must be one of {self.MODELS}")
            self.model = args.model
        else:
            self.model = self.MODELS[0]
            # Update the args object so that the model name will be included in the logs
            args.model = self.model
        self.system_message = system_message
        self.messages += self.get_initial_messages()
        self.in_price = MODEL_INFO[self.NAME][self.args.model].get("cost_per_input_token", 0)
        self.out_price = MODEL_INFO[self.NAME][self.args.model].get("cost_per_output_token", 0)

    def setup(self):
        status.system_message(self.system_message)

    def get_initial_messages(self):
        return [
            self._system_message(self.system_message),
        ]

    @classmethod
    def get_models(cls):
        return cls.MODELS

    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
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


    def parse_tool_calls(self, tool_calls) -> dict:
        # TODO implement properly
        parsed_arguments = json.loads(tool_call.arguments)
        tool_call.parsed_arguments = parsed_arguments
        Formatter.validate_args(tool, tool_call)
        Formatter.convert_args(tool, tool_call)
        return tool_call

    def send(self, message: str) -> Tuple[Optional[str],bool]:
        self.messages.append(self._user_message(message))
        response = self._call_model()
        self.messages.append(response)
        in_token = count_token(message=message, model=self.args.model)
        out_token = count_token(message=response.content, model=self.args.model)
        cost = in_token * self.in_price + out_token * self.out_price

        # TODO implement a parse_tool_calls
        tool_calls = self.parse_tool_calls(response.tool_calls)
        return response.content, tool_calls, cost

    def get_system_message(self):
        self.system_message
