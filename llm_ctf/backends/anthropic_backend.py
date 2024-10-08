from argparse import Namespace
from anthropic import Anthropic, RateLimitError
from .utils import *
import os
from anthropic.types.content_block import ContentBlock as AnthropicMessage
from .vllm_backend import VLLMBackend
from ..tools import Tool, ToolCall, ToolResult
from ..prompts.prompts import PromptManager
from .backend import UserMessage

class AnthropicBackend(VLLMBackend):
    NAME = 'anthropic'
    MODELS = list(MODEL_INFO[NAME].keys())
    QUIRKS = {key: NO_QUIRKS for key in MODELS}
    API_KEY_PATH = "~/.config/anthropic/api_key"

    def __init__(self, system_message: str, hint_message: str, tools: dict[str, Tool], prompt_manager: PromptManager, model=None, api_key=None, args: Namespace = None):
        super().__init__(system_message, hint_message, tools, prompt_manager, model=model, api_key=api_key, args=args)
        self.in_price = MODEL_INFO[self.NAME][self.model].get("cost_per_input_token", 0)
        self.out_price = MODEL_INFO[self.NAME][self.model].get("cost_per_output_token", 0)

    def client_setup(self):
        if self.api_key:
            api_key = self.api_key
        elif KEYS and "ANTHROPIC_API_KEY" in KEYS:
            api_key = KEYS["ANTHROPIC_API_KEY"].strip()
        elif "ANTHROPIC_API_KEY" in os.environ:
            api_key = os.environ["ANTHROPIC_API_KEY"]
        elif os.path.exists(os.path.expanduser(self.API_KEY_PATH)):
            api_key = open(os.path.expanduser(self.API_KEY_PATH), "r").read().strip()
        else:
            raise ValueError(f"No Anthropic API key provided and none found in ANTHROPIC_API_KEY or {self.API_KEY_PATH}")
        os.environ["ANTHROPIC_API_KEY"] = api_key
        self.client = Anthropic(api_key=api_key.strip('\''))

    def append(self, message : dict|AnthropicMessage|List[ToolResult]):
        if isinstance(message, dict):
            conv_message = message
        elif isinstance(message, list):
            conv_message = self.tool_results_message(message)
        elif isinstance(message, AnthropicMessage):
            conv_message = {
                "role": "assistant",
                "content": message.text,
            }
        else:
            raise ValueError(f"Unknown message type: {type(message)}")
        self.outgoing_messages.append(conv_message)
        self.messages.append(conv_message)

    def send(self, message: str) -> Tuple[Optional[str],List,int]:
        if message:
            self.append(self.user_message(message))
        else:
            message = ""
        _, content = self.call_model()
        # TODO take into account the full prompt and not just this message
        in_token = self.client.count_tokens(message)
        out_token = self.client.count_tokens(content)
        cost = in_token * self.in_price + out_token * self.out_price
        return content, self.last_tool_calls, cost
    
    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
    def _call_model(self, stop_seqs) -> AnthropicMessage:
        return self.client.messages.create(
            model=self.model,
            messages=self.outgoing_messages[1:], # Skip system message
            temperature=1,
            max_tokens=1024,
            stop_sequences=stop_seqs,
            system=self.get_system_message(),
        )

    def call_model_internal(self, start_seqs, stop_seqs):
        start_seqs, stop_seqs = self.formatter.get_delimiters()
        response = self._call_model(stop_seqs)
        if response.stop_reason == "stop_sequence":
            response.content[0].text += response.stop_sequence

        if any(s in response.content[0].text for s in start_seqs):
            has_tool_calls = True
        else:
            has_tool_calls = False
        status.debug_message(f"Response:\n{response.content[0].text}", truncate=False)
        message = response.content[0]
        return response, message.text, message, has_tool_calls
