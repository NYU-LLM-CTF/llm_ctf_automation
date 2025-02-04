from argparse import Namespace
import json
from openai import OpenAI
import os
from typing import List, Optional, Tuple
import tiktoken

from .backend import Backend
from ..formatters import Formatter
from ..tools import Tool, ToolCall, ToolResult
from ..ctflogging import status
from openai import RateLimitError
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall as OAIToolCall
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from .utils import KEYS, MODEL_INFO

import backoff  # for exponential backoff

API_KEY_PATH = "~/.openai/api_key"

def get_tool_calls(otc_calls : List[OAIToolCall]) -> List[ToolCall]:
    if not otc_calls:
        return []
    return [ToolCall.create_unparsed(otc.function.name, otc.id, otc.function.arguments) for otc in otc_calls]

def make_tool_result(res: ToolResult):
    return dict(
        name=res.name,
        role="tool",
        content=json.dumps(res.result),
        tool_call_id=res.id,
    )

class OpenAIBackend(Backend):
    NAME = 'openai'
    MODELS = list(MODEL_INFO[NAME].keys())

    def __init__(self, system_message: str, hint_message: str, tools: dict[str,Tool], model: str = None, api_key: str = None, args: Namespace = None):
        if api_key is None:
            if KEYS and "OPENAI_API_KEY" in KEYS:
                api_key = KEYS["OPENAI_API_KEY"].strip()
            elif "OPENAI_API_KEY" in os.environ:
                api_key = os.environ["OPENAI_API_KEY"]
            elif os.path.exists(os.path.expanduser(API_KEY_PATH)):
                api_key = open(os.path.expanduser(API_KEY_PATH), "r").read().strip()
            else:
                raise ValueError(f"No OpenAI API key provided and none found in OPENAI_API_KEY or {API_KEY_PATH}")
        self.client = OpenAI(api_key=api_key.strip('\''))
        self.tools = tools
        self.args = args
        self.tool_schemas = [ChatCompletionToolParam(**tool.schema) for tool in tools.values()]
        if model is None:
            self.model = self.MODELS[0]
        else:
            if model not in self.MODELS:
                raise ValueError(f"Invalid model {model}. Must be one of {self.MODELS}")
            self.model = model
        self.system_message = system_message
        self.hint_message = hint_message
        self.messages += self.get_initial_messages()
        self.in_price = MODEL_INFO[self.NAME][self.model].get("cost_per_input_token", 0)
        self.out_price = MODEL_INFO[self.NAME][self.model].get("cost_per_output_token", 0)
        self.token_encoding = tiktoken.encoding_for_model(model_name=self.model)

    def setup(self):
        status.system_message(self.system_message)
        if self.args.hints:
            status.hint_message(self.hint_message)

    def get_initial_messages(self):
        messages = [
            self._system_message(self.system_message),
        ]
        if self.args.hints:
            messages.append(self._hint_message(self.hint_message))
        return messages

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
            "role": "user" if role == "hint" else role,
            "content": content,
            "hint": role == 'hint',
        }

    def _user_message(self, content : str) -> dict[str,str]:
        return self._message(content, "user")

    def _system_message(self, content : str) -> dict[str,str]:
        return self._message(content, "system")

    def _hint_message(self, content: str) -> dict[str, str]:
        return self._message(content, "hint")

    def count_tokens(self, message: Optional[str]):
        if not message:
            return 0
        return len(self.token_encoding.encode(message))

    def parse_tool_arguments(self, tool: Tool, tool_call: ToolCall) -> Tuple[bool, ToolCall | ToolResult]:
        # Don't need to parse if the arguments are already parsed;
        # this can happen if the tool call was created with parsed arguments
        if tool_call.parsed_arguments:
            return True, tool_call
        try:
            tool_call.parsed_arguments = json.loads(tool_call.arguments)
            Formatter.validate_args(tool, tool_call)
            Formatter.convert_args(tool, tool_call)
            return True, tool_call
        except json.JSONDecodeError as e:
            status.debug_message(f"Error decoding arguments for {tool.name}: {e}")
            status.debug_message(f"Arguments: {tool_call.arguments}")
            tool_res = tool_call.error(f"{type(e).__name__} decoding arguments for {tool.name}: {e}")
            return False, tool_res
        except ValueError as e:
            msg = f"Error extracting parameters for {tool.name}: {e}"
            status.debug_message(msg)
            tool_res = tool_call.error(msg)
            return False, tool_res

    def append(self, message : dict|List[ToolResult]):
        if isinstance(message, list):
            self.messages.extend([make_tool_result(r) for r in message])
        else:
            self.messages.append(message)

    def send(self, message: Optional[str]=None) -> Tuple[Optional[str],bool]:
        if message:
            self.append(self._user_message(message))
        response = self._call_model()
        self.append(response)
        in_token = self.count_tokens(message)
        out_token = self.count_tokens(response.content)
        cost = in_token * self.in_price + out_token * self.out_price
        return response.content, get_tool_calls(response.tool_calls), cost

    def get_system_message(self):
        self.system_message
