from abc import ABC, abstractmethod
from typing import List, Tuple, Type

from ..prompts import PromptManager
from ..ctflogging import status
from ..utils import str2bool
from ..tools import Tool, ToolCall, ToolResult

class Formatter(ABC):
    NAME : str
    prompt_manager = None
    render_delimiters = True
    code_blocks = True
    delims_in_code_block = False

    registry = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[cls.NAME] = cls

    @abstractmethod
    def format_tools(self, tools : List[Tool]) -> str:
        """Format a list of available tools for use in a prompt"""
        raise NotImplementedError

    @abstractmethod
    def format_results(self, results : List[ToolResult]) -> str:
        """Format the results of running tools"""
        raise NotImplementedError

    @abstractmethod
    def format_tool_calls(self, tool_calls : List[ToolCall], placeholder : bool = False) -> str:
        """Format tool calls for use in a prompt.

        If placeholder is True, assume only one tool call is being formatted and
        add ellipses to indicate that more parameters can be used.

        Example (from the XML formatter):
        <function_calls>
        <invoke>
        <tool_name>$TOOL_NAME</tool_name>
        <call_id>$CALL_ID</call_id>
        <$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
        ...
        </invoke>
        """
        raise NotImplementedError

    def tool_use_prompt(self) -> str:
        """Generate a tool use prompt"""
        prompt = self.prompt_manager.tool_use(
            self,
            self.tools.values(),
            ToolCall.create_parsed("$TOOL_NAME", "$CALL_ID", {"$PARAMETER_NAME": "$PARAMETER_VALUE"})
        )
        return prompt

    def tool_call_prompt(self, tool_calls : List[ToolCall]) -> str:
        """Generate a tool calls prompt"""
        return self.prompt_manager.tool_calls(self, tool_calls)

    def tool_result_prompt(self, results : List[ToolResult]) -> str:
        """Generate a tool result prompt"""
        return self.prompt_manager.tool_results(self, results)

    @abstractmethod
    def extract_content(self, message) -> str:
        """Extract the content of a message (without tool calls)"""
        raise NotImplementedError

    @abstractmethod
    def extract_tool_calls(self, message) -> List[ToolCall]:
        """Extract tool calls from a message"""
        raise NotImplementedError

    @abstractmethod
    def extract_params(self, tool : Tool, invocation: ToolCall) -> ToolCall:
        """Extract and validate parameters from a tool call.

        The returned ToolCall should have the same structure as the input ToolCall,
        but with the parsed_arguments field filled in.
        """
        raise NotImplementedError

    @abstractmethod
    def get_delimiters(self) -> Tuple[List[str],List[str]]:
        """Return the start and stop delimiters for tool calls.

        Returns (start_delimiters, stop_delimiters).
        """
        raise NotImplementedError

    @classmethod
    def from_name(cls, name : str) -> Type['Formatter']:
        """Get a formatter class by name"""
        return cls.registry[name.lower()]

    @classmethod
    def names(cls) -> List[str]:
        """Get a list of available formatter names"""
        return list(cls.registry.keys())

    @classmethod
    def classes(cls) -> List[Type['Formatter']]:
        """Get a list of available formatter classes"""
        return list(cls.registry.values())

    @property
    def name(self):
        return self.NAME

    @property
    def start_seqs(self):
        return self.get_delimiters()[0]

    @property
    def stop_seqs(self):
        return self.get_delimiters()[1]

    @classmethod
    def validate_args(cls, tool : Tool, tool_call: ToolCall):
        """Validate the arguments of a parsed tool call.

        This function raises ValueError for missing arguments and prints a warning
        for extra arguments. The extra arguments are removed from the invocation.

        If you want to do additional validation, override this
        method in a subclass.

        Returns a set of extra arguments in case they need to be removed.
        """
        params = set(tool.parameters.keys())
        required = tool.required_parameters
        args = set(tool_call.function.parsed_arguments.keys())
        # Check for missing required arguments
        if missing := (required - args):
            raise ValueError(f"Missing required arguments in call to {tool.name}: {missing}")
        # Check for extra arguments
        if extra := (args - params):
            status.debug_message(f"Warning: extra arguments in call to {tool.name}: {extra}")
            for k in extra:
                del tool_call.function.parsed_arguments[k]
        return extra

    @classmethod
    def convert_args(cls, tool : Tool, tool_call: ToolCall):
        """Convert the parsed arguments of a tool call to the correct types.

        This function assumes that the arguments have already been validated,
        and that they are either already converted or are strings.

        Modifies the invocation in place.
        """
        conversions = {
            (str,bool) : str2bool,
        }
        parsed_args = tool_call.function.parsed_arguments
        for k,v in parsed_args.items():
            if k not in tool.parameters:
                # Ignore extra parameters
                continue

            python_type = tool.parameters[k]['python_type']
            if not isinstance(type(v), python_type):
                if (type(v),python_type) in conversions:
                    parsed_args[k] = conversions[(type(v),python_type)](v)
                else:
                    # Fall back to just using the annotation's type
                    parsed_args[k] = python_type(v)
