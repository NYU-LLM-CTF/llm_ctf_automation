from abc import ABC, abstractmethod
from typing import Any, Tuple, Type, List
from ..utils import timestamp
from ..ctflogging import status

class Backend(ABC):
    """
    Base class for backends. A backend is responsible for running tools and
    communicating with the model.
    """

    NAME: str
    """The name of the backend. This should be unique."""

    timestamps = []
    messages : List[Any] = []
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
    def run_tools(self) -> Tuple[str,bool]:
        """
        Run tools, send the results to the model, and return its response.

        Returns:
            (content, has_tool_calls) where has_tool_calls is True if the
            model wants to run more tools.
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

    @abstractmethod
    def get_message_log(self) -> List[dict]:
        """
        Get the messages that have been sent and received so far.
        Subclasses should override this to format their message log
        for dumping to JSON.
        """
        raise NotImplementedError

    def add_message(self, message):
        """Add a message to the log."""
        self.timestamps.append(timestamp())
        self.messages.append(message)

    def get_timestamped_messages(self):
        """Get the converted messages in the log with timestamps."""
        messages = self.get_message_log()
        if len(self.timestamps) != len(messages):
            status.debug_message(f"{len(self.timestamps)=}, {len(messages)=}", truncate=False)
            status.debug_message(f"Timestamps: {self.timestamps}", truncate=False)
            status.debug_message(f"Messages: {messages}", truncate=False)
        return list(zip(self.timestamps, messages))

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
