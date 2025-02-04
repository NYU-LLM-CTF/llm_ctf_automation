import json
import copy

from dataclasses import dataclass
from typing_extensions import Annotated
from typing import TYPE_CHECKING, Any, Optional, Set, get_type_hints
from tool_def_generator import ToolDefGenerator
import inspect

from ..utils import CALL_ID
from ..ctflogging import status
# if TYPE_CHECKING:
#     from ..environment import CTFEnvironment

class AllCategories:
    """A class that can be used to indicate that a tool should be available in all categories."""
    pass

ALL = AllCategories()

try:
    from enum import StrEnum
except ImportError:
    # Required for older python versions <=3.10
    from enum import Enum
    class StrEnum(str, Enum):
        pass

class CTFCategories(StrEnum):
    rev = "rev"
    pwn = "pwn"
    crypto = "crypto"
    misc = "misc"
    forensics = "forensics"
    web = "web"
    
# Some helpful classes for tool-related things
@dataclass
class ToolFunction:
    name: str
    """The name of the tool function"""
    arguments: Any
    """The unparsed arguments to the tool function"""
    parsed_arguments: Optional[dict[str,Any]]
    """The parsed arguments to the tool function"""
    
@dataclass
class ToolResult:
    name: str
    """The name of the tool that was run"""
    id: str
    """The ID of the tool call"""
    result: dict[str, Any]
    """The result of running the tool"""

    # Serialize in OpenAI format
    def model_dump(self):
        return dict(
            name=self.name,
            role="tool",
            content=json.dumps(self.result),
            tool_call_id=self.id,
        )

class ToolCall:
    def __init__(self, name, id, arguments=None, parsed_arguments=None):
        if id is None:
            id = CALL_ID()
        self.id = id
        self.function = ToolFunction(name, arguments, parsed_arguments)
        self.type = "function"

    def error(self, message):
        return ToolResult(self.name, self.id, {"error": message})

    @classmethod
    def create_unparsed(cls, name, id, arguments):
        """Create a ToolCall with arguments set."""
        return cls(name, id, arguments=arguments)

    @classmethod
    def create_parsed(cls, name, id, parsed_arguments):
        """Create a ToolCall with parsed_arguments set."""
        return cls(name, id, parsed_arguments=parsed_arguments)

    def parsed_copy(self, parsed_arguments) -> "ToolCall":
        """Returns a copy of this ToolCall with parsed_arguments set."""
        return ToolCall(
            self.name,
            self.id,
            arguments=copy.copy(self.function.arguments) if self.function.arguments else None,
            parsed_arguments=parsed_arguments
        )

    def __str__(self) -> str:
        if self.function.parsed_arguments:
            return f"{self.name}({self.function.parsed_arguments})"
        elif self.function.arguments:
            return f"{self.name}({self.function.arguments})"
        else:
            return f"{self.name}([arguments unset])"

    def __repr__(self) -> str:
        return f"<ToolCall {self.name=}, {self.id=}, {self.function=}>"

    @property
    def arguments(self):
        return self.function.arguments
    @arguments.setter
    def arguments(self, value):
        self.function.arguments = value

    @property
    def parsed_arguments(self):
        return self.function.parsed_arguments
    @parsed_arguments.setter
    def parsed_arguments(self, value):
        self.function.parsed_arguments = value

    def model_dump(self):
        # Serialize in OpenAI format
        if self.parsed_arguments is not None:
            args = json.dumps(self.parsed_arguments)
        else:
            # Trickier; could be anything
            try:
                args = json.dumps(self.arguments)
            except Exception as e:
                args = json.dumps(str(self.arguments))
        return {
            "id": self.id,
            "function": {
                "name": self.name,
                "arguments": args,
            },
            "type": self.type,
        }

    @property
    def name(self):
        return self.function.name

class Tool:
    # Attributes that must be set by subclasses
    NAME : str
    """The name of the tool as it should be displayed to the model"""
    CATEGORIES : Set[CTFCategories]|AllCategories = ALL
    """The categories in which the tool should be available"""

    # Automatically generated attributes
    schema : dict[str,Any]
    """The schema for the tool, generated from the __call__ method's annotations"""
    description : str
    """The description of the tool"""
    parameters : dict[str,Any]
    """The parameters of the tool"""
    required_parameters : set[str]
    """The required parameters of the tool"""
    
    @classmethod
    def get_all_subclasses(cls):
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            subclasses.extend(subclass.get_all_subclasses())
        return subclasses

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.name = cls.NAME
        # Automatically generate the schema from the __call__ method's annotations
        generator = ToolDefGenerator(name_mappings=[(cls.__call__.__qualname__, cls.NAME)])
        cls.schema = generator.generate(cls.__call__)[0]
        # Some convenience attributes
        cls.description = cls.schema['function']['description']
        cls.required_parameters = set(cls.schema['function']['parameters']['required'])
        cls.parameters = {}
        hints = get_type_hints(cls.__call__)
        for p,v in inspect.signature(cls.__call__).parameters.items():
            if p == 'self': continue
            cls.parameters[p] = cls.schema['function']['parameters']['properties'][p].copy()
            cls.parameters[p]['name'] = p
            cls.parameters[p]['required'] = p in cls.schema['function']['parameters']['required']
            if v.default is not inspect.Parameter.empty:
                cls.parameters[p]['default'] = v.default
                cls.parameters[p]['required'] = False
            cls.parameters[p]['python_type'] = hints[p]

    def __init__(self):
        pass

    @classmethod
    def make_call(cls, id: Optional[str] = None, **kwargs) -> ToolCall:
        """Create a ToolCall for this tool, instantiating the function with the given arguments"""
        return ToolCall.create_parsed(cls.name, id, kwargs)

    def run(self, tc : ToolCall) -> ToolResult:
        """Run the tool on a parsed ToolCall, returning a ToolResult"""
        if tc.function.parsed_arguments is None:
            raise ValueError("ToolCall must have parsed_arguments set")
        result = self(**tc.function.parsed_arguments)
        return ToolResult(tc.name, tc.id, result)

    def __call__(self, **kwargs):
        """Implementation of the tool."""
        raise NotImplementedError

    def setup(self):
        """Set up the tool."""
        pass

    def teardown(self, exc_type, exc_value, traceback):
        """
        Tear down the tool.

        Called from __exit__ in the CTFEnvironment context manager; if an
        exception occurred, exc_type, exc_value, and traceback will be set
        to the exception information.
        """
        pass

    def __repr__(self):
        return f"<Tool {self.name}>"
