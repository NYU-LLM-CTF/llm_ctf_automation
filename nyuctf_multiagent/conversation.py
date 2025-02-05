from dataclasses import dataclass, replace
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

    def dump(self):
        """
        Dump message to serialize to json.
        """
        d = {"role": str(self.role), "index": self.index, "content": self.content}
        if self.role == MessageRole.ASSISTANT and self.tool_data is not None:
            if self.tool_data.parsed_arguments is not None:
                d["tool_call"] = {"name": self.tool_data.name, "parsed_args": self.tool_data.parsed_arguments}
            else:
                d["tool_call"] = {"name": self.tool_data.name, "args": self.tool_data.arguments}
        elif self.role == MessageRole.OBSERVATION and self.tool_data is not None:
            d["tool_result"] = {"name": self.tool_data.name, "result": self.tool_data.result}
        return d

class Conversation:
    """Holds the messages of the entire conversation"""

    def __init__(self, name="", truncate_content=25000, len_observations=None):
        """
        truncate_content: truncate the OBSERVATION content length to these many characters.
        len_observations (int):
            Return last `len_observations` observations and truncate the rest in get_messages.
            None (default) means return all. This helps truncate the conversation to last few steps.
        """
        self.all_messages = []        
        self.round = 0
        self.name = name
        self.truncate_content = truncate_content
        self.len_observations = len_observations

    @property
    def messages(self):
        """
        Generator of messages of this conversation to send to the LLM for completion
        """
        
        trunc_before = -1
        if self.len_observations is not None:
            trunc_before = self.round - self.len_observations
        for m in self.all_messages:
            if m.role == MessageRole.OBSERVATION and m.index <= trunc_before:
                # Truncate observations
                continue
            elif m.role == MessageRole.ASSISTANT and m.index <= trunc_before:
                if m.content is not None:
                    # Remove tool calls from assistant actions and yield only thought
                    yield replace(m, tool_data=None)
                else:
                    # Without tool_call, message is empty so skip
                    continue
            else:
                yield m

    def dump(self):
        """
        Dump all messages to serialize to json.
        """
        return [m.dump() for m in self.all_messages]

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
        # Truncate length
        truncate_message = " ...very long output, trunctated!"
        if type(tool_data.result) == str and len(tool_data.result) > self.truncate_content:
            tool_data.result = tool_data.result[:self.truncate_content - len(truncate_message)] + truncate_message
        elif type(tool_data.result) == dict:
            for key in tool_data.result.keys():
                if type(tool_data.result[key]) == str and len(tool_data.result[key]) > self.truncate_content:
                    tool_data.result[key] = tool_data.result[key][:self.truncate_content - len(truncate_message)] + truncate_message

        self.append(MessageRole.OBSERVATION, None, tool_data)
