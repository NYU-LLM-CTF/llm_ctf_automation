from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional, Tuple, Type, List, Union
from ..tools import Tool, ToolCall, ToolResult
from ..utils import timestamp

class IterKind(Enum):
    # May be skipped in iteration if item.skips is True
    MAY_SKIP = 1
    # Include in the iteration
    KEEP = 2
    # Include in the iteration, but only the last one;
    # item.finish_collect will be called with all items of the same kind
    COLLECT = 3

# Our log format expects the messages to follow the chat completion message format
# from OpenAI; we allow an 'extra' field for storing information about the original
# message from non-OpenAI backends.

@dataclass
class FakeToolCalls:
    """ToolCalls that were created for a demo message; they lack a response"""
    tool_calls : List[ToolCall]
    content : Optional[str] = None

    def model_dump(self):
        return {
            'role': 'assistant',
            'content': self.content,
            'tool_calls': [tc.model_dump() for tc in self.tool_calls],
        }

def make_extra(obj, *fields):
    extra_fields = {}
    for field in fields:
        data = getattr(obj, field)
        data = data.model_dump() if hasattr(data, 'model_dump') else data
        data_type = type(data).__name__
        extra_fields[field] = {'type': data_type, 'data': data}
    return {
        'type': type(obj).__name__,
        **extra_fields,
    }

@dataclass
class UnparsedToolCalls:
    response: Any
    tool_calls: List[ToolCall]
    content: Optional[str] = None
    def model_dump(self):
        return {
            'role': 'assistant',
            'content': self.content,
            'tool_calls': [tc.model_dump() for tc in self.tool_calls],
            'extra': make_extra(self, 'response'),
        }

class ParsedToolCalls(UnparsedToolCalls):
    pass

@dataclass
class ErrorToolCalls:
    response: Any
    error: str
    content: Optional[str] = None
    def model_dump(self):
        return {
            'role': 'assistant',
            'content': self.content,
            'tool_calls': [],
            'extra': make_extra(self, 'response', 'error'),
        }

@dataclass
class UserMessage:
    content: str
    role: Literal["user"] = "user"
    def model_dump(self):
        return vars(self)
    
@dataclass
class HintMessage:
    content: str
    role: Literal["user"] = "user"
    def model_dump(self):
        return {
            'role': 'user',
            'content': self.content,
            'hint': True,
        }

@dataclass
class SystemMessage:
    content: str
    role: Literal["system"] = "system"
    tool_use_prompt: Optional[str] = None
    def model_dump(self):
        return {
            'role': 'system',
            'content': self.content,
            'extra': make_extra(self, 'tool_use_prompt'),
        }

@dataclass
class AssistantMessage:
    content: str
    role: Literal["assistant"] = "assistant"
    response: Optional[Any] = None
    def model_dump(self):
        return {
            'role': 'assistant',
            'content': self.content,
            'extra': make_extra(self, 'response'),
        }

MessageTypes = Union[FakeToolCalls, UnparsedToolCalls, ParsedToolCalls, ToolResult,
                     ErrorToolCalls, UserMessage, SystemMessage, AssistantMessage]

class TimestampedList(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.timestamps = []
        for i in range(len(self)):
            self.timestamps.append(timestamp())

    def append(self, item):
        super().append(item)
        self.timestamps.append(timestamp())

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __add__(self, other):
        result = TimestampedList(self)
        result.extend(other)
        return result

    def __getitem__(self, index):
        if isinstance(index, slice):
            result = TimestampedList(super().__getitem__(index))
            result.timestamps = self.timestamps[index]
            return result
        else:
            return super().__getitem__(index)

    def get_timestamped(self):
        return zip(self.timestamps, self)

    @property
    def safe(self):
        """Iterator for a version of this list suitable for logging"""
        collected : List[MessageTypes] = []
        current_kind = None

        def finish_run():
            if collected:
                combined = collected[-1].finish_collect(collected, current_kind)
                yield combined
                collected.clear()

        for item in self:
            if item.iter_kind == IterKind.KEEP:
                yield from finish_run()
                yield item
            elif item.iter_kind == IterKind.MAY_SKIP and item.skips:
                if not collected or (collected and item.item_kind != current_kind):
                    continue
            elif item.iter_kind == IterKind.COLLECT:
                if collected and type(item) != current_kind:
                    yield from finish_run()
                collected.append(item)
                current_kind = type(item)
            else:
                raise ValueError(f"Unknown iter kind: {item.iter_kind}")
        # Finish tail
        yield from finish_run()

class Backend(ABC):
    """
    Base class for backends. A backend is responsible for communicating with the model.
    """

    NAME: str
    """The name of the backend. This should be unique."""

    _messages : TimestampedList[Any] = TimestampedList()
    """
    The messages that have been sent and received so far. Each message is a
    tuple of the time it was sent/received and the content of the message.
    """

    registry = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[cls.NAME] = cls

    def setup(self):
        """
        Perform any necessary setup before starting the conversation.
        """
        pass

    @abstractmethod
    def parse_tool_arguments(self, tool: Tool, tool_call: ToolCall) -> Tuple[bool, ToolCall | ToolResult]:
        """Extract and parse the parameters for a tool call.

        Returns:
        - (True, tool_call) if successful; the tool_call's parsed_arguments will be set in-place
        - (False, tool_result) if unsuccessful; the tool_result will contain an error message
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, content: str) -> Tuple[str,bool]:
        """
        Send a message to the model and return the response.

        Returns:
            (content, has_tool_calls) where has_tool_calls is True if the
            model wants to run tools.
        """
        raise NotImplementedError

    def get_timestamped_messages(self):
        """Get the converted messages in the log with timestamps."""
        converted = []
        for ts,m in self.messages.get_timestamped():
            converted.append((ts, m.model_dump() if hasattr(m, 'model_dump') else m))
        # Add the system message if the first message isn't a system message
        if converted[0][1]['role'] != 'system':
            converted.insert(
                0, (converted[0][0], {'role': 'system', 'content': self.get_system_message()})
            )
        return converted

    @classmethod
    @abstractmethod
    def get_models(cls) -> List[str]:
        """
        Get the available models for this backend.
        """
        raise NotImplementedError

    @classmethod
    def from_name(cls, name : str) -> Type['Backend']:
        return cls.registry[name.lower()]

    @classmethod
    def names(cls) -> List[str]:
        """Get a list of available backend names"""
        return list(cls.registry.keys())

    @classmethod
    def classes(cls) -> List[Type['Backend']]:
        """Get a list of available backend classes"""
        return list(cls.registry.values())

    @property
    def messages(self):
        return self._messages
    @messages.setter
    def messages(self, value):
        self._messages = TimestampedList(value)

    @abstractmethod
    def get_system_message(self):
        raise NotImplementedError

class NotGiven:
    pass
NOT_GIVEN = NotGiven()

@dataclass
class SamplingParams:
    temperature: Optional[float|NotGiven] = NOT_GIVEN
    frequency_penalty: Optional[float|NotGiven] = NOT_GIVEN
    max_tokens: Optional[int|NotGiven] = NOT_GIVEN
    presence_penalty: Optional[float|NotGiven] = NOT_GIVEN
    top_p: Optional[int|NotGiven] = NOT_GIVEN
