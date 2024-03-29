from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Type
from ..tools import Tool, ToolCall, ToolResult

class Formatter(ABC):
    NAME : str

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
