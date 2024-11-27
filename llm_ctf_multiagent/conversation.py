from dataclasses import dataclass
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    OBSERVATION = "observation"


@dataclass(frozen=True)
class Message:
    """Holds message contents"""
    index: int
    role: MessageRole
    content: str
    tool_data: dict = None

class Conversation:
    """Holds the messages of the entire conversation"""

    def __init__(self, name=""):
        self.all_messages = []        
        self.round = 0
        self.name = name

    def get_messages(self, len_observations=None):
        """
        Get messages of this conversation to send to the LLM for completion

        len_observations (int):
            Return last `len_observations` observations and truncate the rest.
            None (default) means return all. This helps truncate the conversation to last few steps.
        Returns:
            generator of the truncated messages
        """
        
        trunc_before = -1
        if len_observations is not None:
            trunc_before = self.round - len_observations
        for m in self.all_messages:
            if m.role == MessageRole.OBSERVATION and m.index <= trunc_before:
                # Truncate
                continue
            yield m

    def next_round(self):
        self.round += 1
    def append(self, role, content, tool_data=None):
        m = Message(index=self.round, role=role, content=content, tool_data=tool_data)
        self.all_messages.append(m)
    def append_system(self, content):
        self.append(MessageRole.SYSTEM, content)
    def append_user(self, content):
        self.append(MessageRole.USER, content)
    def append_assistant(self, content, tool_data):
        self.append(MessageRole.ASSISTANT, content, tool_data)
    def append_observation(self, tool_data):
        self.append(MessageRole.OBSERVATION, None, tool_data)
