import json
from openai import OpenAI, RateLimitError
from openai.types.chat import ChatCompletionMessage

from ..conversation import MessageRole
from ..tools import ToolCall

class OpenAIBackend:
    NAME = 'openai'
    # MODELS = list(MODEL_INFO[NAME].keys())

    def __init__(self, model, tools, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.tools = tools
        self.model = model
        self.tool_schemas = [self.get_tool_schema(tool) for tool in tools.values()]

        self.in_price = 0 # TODO load
        self.out_price = 0 # TODO load
        # TODO self.token_encoding = tiktoken.encoding_for_model(model_name=self.model)

    @staticmethod
    def get_tool_schema(tool):
        # Based on required OpenAI format, https://platform.openai.com/docs/guides/function-calling
        return {
            "type": "function",
            "function": {
                "name": tool.NAME,
                "description": tool.DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {n: {"type": p[0], "description": p[1]} for n, p in tool.PARAMETERS.items()},
                    "required": list(tool.REQUIRED_PARAMETERS),
                }
            }
        }

    # @backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
    def _call_model(self, messages) -> ChatCompletionMessage:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_schemas,
            tool_choice="auto", # TODO try "required" here to force a function call
            parallel_tool_calls=False
        ).choices[0].message

    # def count_tokens(self, message: Optional[str]):
    #     if not message:
    #         return 0
    #     return len(self.token_encoding.encode(message))

    def parse_tool_arguments(self, tool_call):
        # Don't need to parse if the arguments are already parsed;
        # this can happen if the tool call was created with parsed arguments
        if tool_call.parsed_arguments:
            return True, tool_call
        try:
            tool_call.parsed_arguments = json.loads(tool_call.arguments)
            self.tools[tool_call.name].validate_params(tool_call)
            return True, tool_call
        except json.JSONDecodeError as e:
            tool_res = ToolResult.for_call(tool_call,
                                           f"{type(e).__name__} while decoding parameters for {tool.NAME}: {e}")
            return False, tool_res
        except ValueError as e:
            msg = f"Error in parameters for {tool.NAME}: {e}"
            tool_res = ToolResult.for_call(tool_call, msg)
            return False, tool_res

    def send(self, messages):
        # formatted_messages = messages # TODO process
        formatted_messages = []
        for m in messages:
            if m.role == MessageRole.OBSERVATION:
                msg = {"role": "tool",
                       "content": json.dumps(m.tool_data.result),
                       "tool_call_id": m.tool_data.id}
            elif m.role == MessageRole.ASSISTANT:
                msg = {"role": m.role.value}
                if m.content is not None:
                    msg["content"] = m.content
                if m.tool_data is not None:
                    msg["tool_calls"] = [{"id": m.tool_data.id,
                                          "type": "function",
                                          "function": {
                                              "name": m.tool_data.name,
                                              "arguments": m.tool_data.arguments
                                            }}]
            else:
                msg = {"role": m.role.value, "content": m.content}
            formatted_messages.append(msg)

        response = self._call_model(formatted_messages)
        if response.tool_calls and len(response.tool_calls) > 0:
            oai_call = response.tool_calls[0]
            tool_call = ToolCall(name=oai_call.function.name, id=oai_call.id,
                                 arguments=oai_call.function.arguments)
        else:
            tool_call = None

        return response.content, tool_call

        # in_token = self.count_tokens(message)
        # out_token = self.count_tokens(response.content)
        # cost = in_token * self.in_price + out_token * self.out_price
