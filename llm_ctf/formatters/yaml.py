from argparse import Namespace
from io import StringIO
import re

from ..prompts import PromptManager
from ..tools.modules import Tool, ToolCall, ToolResult
from ..utils import CALL_ID
from ..ctflogging import status
from .formatter import Formatter
from typing import Dict, List, Any, Tuple
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from collections.abc import Sequence

def _md(text: str) -> str:
    return f"```yaml\n{text}\n```"

TOOL_USE_START = '----- BEGIN TOOL CALLS -----'
TOOL_USE_STOP = '----- END TOOL CALLS -----'

class YAMLFormatter(Formatter):
    NAME = 'yaml'

    def __init__(self, tools: dict[str,Tool], prompt_set='default'):
        self.yaml = YAML()
        # Need to have the list of possible tools so we can use param names to try and
        # fix up the YAML if it's broken
        self.tools = tools
        self._tool_string_param_names = set()
        for tool in tools.values():
            for param_name, param_props in tool.parameters.items():
                if param_props['type'] == 'string':
                    self._tool_string_param_names.add(param_name)
        self.prompt_manager = PromptManager(prompt_set)
        self.render_delimiters = True
        self.code_blocks = True
        self.delims_in_code_blocks = False

    def _dump(self, data: dict) -> str:
        o = StringIO()
        self.yaml.dump(data, o)
        return o.getvalue()

    def _tool_dict(self, tool: Tool) -> dict:
        # NB - all the dictionary insertions are done one at a time so that we can
        # control the order; Python 3.7+ guarantees that insertion order is preserved
        tool_dict = {}
        tool_dict["name"] = tool.name
        tool_dict["description"] = tool.description
        tool_dict["parameters"] = {}
        for name, info in tool.parameters.items():
            param = {}
            param["type"] = info['type']
            param["description"] = info['description']
            param["required"] = info['required']
            tool_dict["parameters"][name] = param
            return tool_dict

    # adapted from AlphaCodium:
    #   https://github.com/Codium-ai/AlphaCodium/blob/3f8ef0054c17c3924efab828ceaedd57bb78aa9a/alpha_codium/gen/utils.py#L133
    def _try_fix_yaml(self, response_text: str, original_exception: Exception):
        response_text_lines = response_text.split('\n')

        keys = self._tool_string_param_names
        response_text_lines_copy = response_text_lines.copy()
        for i in range(0, len(response_text_lines_copy)):
            for key in keys:
                if response_text_lines_copy[i].strip().startswith(key) and not '|' in response_text_lines_copy[i]:
                    response_text_lines_copy[i] = response_text_lines_copy[i].replace(f'{key}',
                                                                                    f'{key} |-\n        ')
        try:
            data = self.yaml.load('\n'.join(response_text_lines_copy))
            return data
        except:
            raise ValueError("Error decoding tool calls as YAML: " + str(original_exception))

    def format_tools(self, tools : List[Tool]) -> str:
        tools_list = [ self._tool_dict(tool) for tool in tools ]
        return self._dump(tools_list)

    def format_results(self, results : List[ToolResult]):
        result_dicts = [
            {
                "tool_name": r.name,
                "call_id": r.id,
                **r.result
            }
            for r in results
        ]
        for d in result_dicts:
            # Prefer multiline literals for string results
            for k,v in d.items():
                if k not in ["tool_name", "call_id"] and isinstance(v, str):
                    d[k] = LiteralScalarString(d[k])
        return self._dump(result_dicts)

    def format_tool_calls(self, tool_calls : List[ToolCall], placeholder : bool = False):
        tool_call_list = []
        for tc in tool_calls:
            d = {}
            d["tool_name"] = tc.name
            d["call_id"] = tc.id
            d.update(tc.function.parsed_arguments)
            tool_call_list.append(d)

        yaml_str = self._dump(tool_call_list)
        if placeholder:
            yaml_lines = yaml_str.split('\n')
            # We want to add a comment with an ellipsis after the placeholder parameter. In theory
            # ruamel should be able to do this via
            #   tool_call_list[0].yaml_set_comment_before_after_key(v, after='...', after_indent=2)
            # but that doesn't do anything. So we just paste it in manually.
            for i in range(len(yaml_lines)):
                v = next(iter(tool_calls[0].function.parsed_arguments.values()))
                if yaml_lines[i].endswith(v):
                    indent = len(yaml_lines[i]) - len(yaml_lines[i].lstrip())
                    yaml_lines.insert(i+1, ' '*indent + "# ...")
                    break
            yaml_str = '\n'.join(yaml_lines)
        return yaml_str

    def extract_content(self, message):
        content = message.split(TOOL_USE_START)[0].strip()
        if not content: content = None
        return content

    def extract_tool_calls(self, message) -> List[ToolCall]:
        md_tc = None
        md_blocks = re.findall(r'```yaml\n(.*?)\n```', message, re.DOTALL)
        if not md_blocks:
            md_blocks = re.findall(r'```\n(.*?)\n```', message, re.DOTALL)

        tc_blocks = []
        for md in md_blocks:
            if 'tool_name' in md:
                tc_blocks.append(md)
        if md_blocks and not tc_blocks:
            status.debug_message("Warning: markdown blocks present but no tool calls found; check?")
            return []
        if len(tc_blocks) > 1:
            status.debug_message("Warning: multiple tool calls found in message; using first")
        md_tc = tc_blocks[0]

        try:
            data = self.yaml.load(md_tc)
        except Exception as e:
            data = self._try_fix_yaml(md_tc, e)

        # Make sure data is a list of dictionaries
        assert isinstance(data, Sequence)
        tool_calls = []
        for item in data:
            id = item.get("call_id")
            name = item.get("tool_name", "[not provided]")
            del item["call_id"]
            del item["tool_name"]
            arguments = item
            tool_calls.append(ToolCall.create_unparsed(name, id, arguments))
        return tool_calls

    def extract_params(self, tool : Tool, tc: ToolCall) -> ToolCall:
        """Extract and validate parameters from a tool call args"""
        args = tc.function.arguments
        # The args coming out of the YAML should already be parsed
        parsed_tc = ToolCall.create_parsed(tc.name, tc.id, args)
        self.validate_args(tool, parsed_tc)
        self.convert_args(tool, parsed_tc)
        return parsed_tc

    def get_delimiters(self):
        """Return the start and stop delimiters for this formatter."""
        return [ TOOL_USE_START ], [ TOOL_USE_STOP ]
