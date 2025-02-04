from argparse import Namespace
import re
from bs4 import BeautifulSoup
from .formatter import Formatter
from ..tools import Tool, ToolCall, ToolResult
from ..prompts import PromptManager
from typing import List, Tuple

TOOL_USE_START = '<function_calls>'
TOOL_USE_STOP = '</function_calls>'

class XMLFormatter(Formatter):
    NAME = 'xml'

    def __init__(self, tools: dict[str,Tool], prompt_manager: PromptManager):
        self.tools = tools
        self.prompt_manager = prompt_manager
        self.render_delimiters = False
        self.code_blocks = True
        self.delims_in_code_block = True

    def format_tool(self, tool : Tool) -> str:
        param_desc = []
        for name, info in tool.parameters.items():
            if info['required']:
                param = f'<parameter required="true">\n'
            else:
                param = f"<parameter>\n"
            param += f"<name>{name}</name>\n"
            param += f"<type>{info['type']}</type>\n"
            param += f"<description>{info['description']}</description>\n"
            param += f"</parameter>"
            param_desc.append(param)

        param_desc = "\n".join(param_desc)
        constructed_prompt = (
            "<tool_description>\n"
            f"<tool_name>{tool.name}</tool_name>\n"
            "<description>\n"
            f"{tool.description}\n"
            "</description>\n"
            "<parameters>\n"
            f"{param_desc}\n"
            "</parameters>\n"
            "</tool_description>"
        )
        return constructed_prompt

    def format_tools(self, tools : List[Tool]) -> str:
        return "<tools>\n" + '\n'.join([self.format_tool(tool) for tool in tools]) + "\n</tools>"

    def format_result(self, tr : ToolResult) -> str:
        res = "\n".join([f"<{key}>{value}</{key}>" for key, value in tr.result.items()])
        return f"<result>\n<tool_name>{tr.name}</tool_name>\n<call_id>{tr.id}</call_id>\n{res}\n</result>"

    def format_results(self, results : List[ToolResult]):
        return ("<function_results>\n" +
                '\n'.join([self.format_result(result) for result in results]) +
                "\n</function_results>")

    def extract_tool_calls(self, message) -> List[ToolCall]:
        soup = BeautifulSoup(message, "lxml")
        invocations = soup.find_all("invoke")
        tool_calls = []
        for invocation in invocations:
            if elem := invocation.find("tool_name"):
                name = elem.text
            else:
                name = "[not provided]"
            if elem := invocation.find("call_id"):
                id = elem.text
            else:
                id = None
            # Defer parsing of parameters until we're actually ready to call the tools
            arguments = invocation
            tool_calls.append(ToolCall.create_unparsed(name, id, arguments))
        return tool_calls

    def format_tool_call(self, tool_call : ToolCall, placeholder : bool = False):
        param_str = "\n".join([
            f"<{key}>{value}</{key}>"
            for key, value in tool_call.function.parsed_arguments.items()
        ])
        if placeholder:
            param_str += '\n...'
        invoke_str = ""
        invoke_str += f"<invoke>\n"
        invoke_str += f"<tool_name>{tool_call.name}</tool_name>\n"
        invoke_str += f"<call_id>{tool_call.id}</call_id>\n"
        invoke_str += f"<parameters>\n"
        invoke_str += param_str + "\n"
        invoke_str += f"</parameters>\n"
        invoke_str += f"</invoke>"
        return invoke_str

    def format_tool_calls(self, tool_calls : List[ToolCall], placeholder : bool = False) -> str:
        return f"{TOOL_USE_START}\n" + "\n".join([
            self.format_tool_call(tc, placeholder)
            for tc in tool_calls
        ]) + f"\n{TOOL_USE_STOP}\n"

    def extract_content(self, message) -> str:
        content = re.split(r'(```xml\s*)?' + re.escape(TOOL_USE_START), message)[0].strip()
        if not content: content = None
        return content

    def extract_params(self, tool : Tool, tc : ToolCall) -> ToolCall:
        invocation : BeautifulSoup = tc.function.arguments
        extracted_parameters = {}
        for param_name in tool.parameters:
            if elem := invocation.find(param_name):
                value = elem.text
                extracted_parameters[param_name] = value
        parsed_tc = ToolCall.create_parsed(tc.name, tc.id, extracted_parameters)
        self.validate_args(tool, parsed_tc)
        self.convert_args(tool, parsed_tc)
        return parsed_tc

    def get_delimiters(self) -> Tuple[List[str],List[str]]:
        """Return the start and stop delimiters for this formatter."""
        return [ TOOL_USE_START ], [ TOOL_USE_STOP ]
