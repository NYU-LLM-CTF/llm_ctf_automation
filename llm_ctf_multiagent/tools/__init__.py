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
        raise NotImplementedError
    def teardown(self):
        raise NotImplementedError

    def validate_params(self, tool_call):
        present = set(tool_call.parsed_arguments.keys())
        if missing := (self.REQUIRED_PARAMETERS - params):
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

    def __str__(self):
        if self.parsed_arguments:
            return f"{self.name}({self.function.parsed_arguments})"
        elif self.arguments:
            return f"{self.name}({self.function.arguments})"
        else:
            return f"{self.name}([arguments unset])"

    def __repr__(self):
        return f"<ToolCall {self.name=}, {self.id=}, {self.function=}>"

@dataclass
class ToolResult:
    name : str
    """The name of the tool that was run"""
    id : str
    """The ID of the tool call"""
    result : str
    """The result of running the tool"""

    @classmethod
    def for_call(tool_call, result):
        """Create a result for a tool_call"""
        return ToolResult(name=tool_call.name, id=tool_call.id, result=result)
