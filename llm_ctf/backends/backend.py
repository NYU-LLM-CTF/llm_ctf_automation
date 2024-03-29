from abc import ABC, abstractmethod
from typing import Tuple, Type, List

class Backend(ABC):
    """
    Base class for backends. A backend is responsible for running tools and
    communicating with the model.
    """

    NAME: str
    """The name of the backend. This should be unique."""

    # message : Message
    # """The message type to use for this backend."""

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
        """
        raise NotImplementedError

    @classmethod
    def from_name(cls, name : str) -> Type['Backend']:
        return cls.registry[name.lower()]
