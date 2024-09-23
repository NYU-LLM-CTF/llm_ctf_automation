from nyuctf.challenge import CTFChallenge

from .formatters import Formatter
from .tools.manager import Tool, ToolCall, ToolResult

def make_call_result(res : ToolResult):
    return dict(
        name=res.name,
        role="tool",
        content=json.dumps(res.result),
        tool_call_id=res.id,
    )

class CTFEnvironment:
    """Manages the docker env for the agent, and the challenge container."""
    def __init__(self, challenge: CTFChallenge):
        # TODO create enter, exit to start dockers and copy files

        self.available_functions = {}
        for tool in TOOLSETS.get(challenge.category, TOOLSETS['default']):
            tool_instance = tool(self.chal)
            self.available_functions[tool_instance.name] = tool_instance

    def __enter__(self):
        for tool in self.available_functions.values():
            tool.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
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

    def run_tools(self, tool_calls) -> Tuple[Optional[str],bool]:
        for tool_call in tool_calls:
            # Tool lookup
            function_name = tool_call.name
            tool = self.tools.get(function_name)
            if not tool:
                tool_call.result = f"Unknown tool {function_name}"
                continue
            tool_call.result = tool.run(tool_call.arguments)

            # # Parameter parsing
            # try:
            #     arguments = self.extract_parameters(tool, tool_call)
            # except json.JSONDecodeError as e:
            #     status.debug_message(f"Error decoding arguments for {function_name}: {e}")
            #     status.debug_message(f"Arguments: {tool_call.function.arguments}")
            #     tool_res = tool_call.error(f"{type(e).__name__} decoding arguments for {function_name}: {e}")
            #     tool_results.append(make_call_result(tool_res))
            #     continue
            # except ValueError as e:
            #     status.debug_message(f"Error extracting parameters for {function_name}: {e}")
            #     tool_res = tool_call.error(
            #         f"{type(e).__name__} extracting parameters for {function_name}: {e}"
            #     )
            #     tool_results.append(make_call_result(tool_res))
            #     continue

            # Tool execution
            # for k,v in tool_res_plain.result.items():
            #     status.debug_message(f"{k}:\n{v}")
            # try:
            #     tool_res = make_call_result(tool_res_plain)
            # except TypeError as e:
            #     status.debug_message(f"Error encoding results from {function_name}: {e}")
            #     tool_res = make_call_result(tool_call.error(
            #         f"{type(e).__name__} running {function_name}: {e}"
            #     ))
            # except Exception as e:
            #     status.debug_message(f"Error running {function_name}: {e}")
            #     tool_res = make_call_result(tool_call.error(
            #         f"{type(e).__name__} running {function_name}: {e}"
            #     ))
        # self.messages += tool_results
        # response = self._call_model()
        # out_token = count_token(message=response.content, model=self.args.model)
        # cost = out_token * self.out_price
        # self.messages.append(response)
        # return response.content, bool(response.tool_calls), cost
