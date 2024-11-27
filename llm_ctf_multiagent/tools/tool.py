from dataclasses import dataclass

class Tool:
    """
    Base class to hold tool definition.
    Attributes that must be set by subclasses.
    """
    NAME: str # The name of the tool as it should be displayed to the model
    DESCRIPTION: str # Description of the tool
    PARAMETERS: dict[str,tuple[str,str]] # Parameters of this model with type and usage explanation
    REQUIRED_PARAMETERS: set[str] # Required parameters

    def __init__(self):
        pass

    # Implement in subclasses
    def call(self, **kwargs):
        raise NotImplementedError
    def setup(self):
        pass
    def teardown(self, ex_type, ex_val, tb):
        pass

    def validate_params(self, tool_call):
        present = set(tool_call.parsed_arguments.keys())
        if missing := (self.REQUIRED_PARAMETERS - present):
            raise ValueError(f"Missing required parameters for {self.NAME}: {missing}")
        # TODO check extra?

class ToolCall:
    """Holds the call and arguments to a specific tool"""
    def __init__(self, name, id=None, arguments=None, parsed_arguments=None):
        if id is None:
            id = CALL_ID()
        self.id = id
        self.name = name
        self.arguments = arguments
        self.parsed_arguments = parsed_arguments

    def error(self, message):
        return ToolResult(self.name, self.id, {"error": message})

    def formatted(self):
        # TODO each tool should format the call individually
        formatted_call = f"**{self.name}:**\n\n"
        if self.parsed_arguments is not None:
            for arg in self.parsed_arguments:
                formatted_call += f"- {arg}: {self.parsed_arguments[arg]}\n"
        elif self.arguments is not None:
            formatted_call += f"{self.arguments}\n"
        else:
            formatted_call += "*no arguments*\n"
        return formatted_call

    def __str__(self):
        if self.parsed_arguments:
            return f"{self.name}({self.parsed_arguments})"
        elif self.arguments:
            return f"{self.name}({self.arguments})"
        else:
            return f"{self.name}([arguments unset])"

    def __repr__(self):
        return f"<ToolCall {self.name=}, {self.id=}, {self.arguments=}>"

@dataclass
class ToolResult:
    name : str
    """The name of the tool that was run"""
    id : str
    """The ID of the tool call"""
    result : str
    """The result of running the tool"""

    @staticmethod
    def for_call(tool_call, result):
        """Create a result for a tool_call"""
        return ToolResult(name=tool_call.name, id=tool_call.id, result=result)
