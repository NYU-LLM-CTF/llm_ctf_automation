from pathlib import Path
from nyuctf.challenge import CTFChallenge

from .conversation import Conversation, MessageRole, Message

now = lambda: time.time()

class BaseAgent:
    def __init__(self, environment, challenge, prompter, backend):
        self.environment = environment
        self.challenge = challenge
        self.prompter = prompter
        self.backend = backend

        self.conversation = Conversation()

        self.conversation.append_system(self.prompter.get("system"))
        self.conversation.append_user(self.prompter.get("initial"))

        self.max_rounds = 3

    def run(self):
        while self.conversation.round <= self.max_rounds:
            response, tool_call = self.backend.send(self.conversation.get_messages(len_observations=5))
            self.conversation.append_assistant(content=response, tool_data=tool_call)

            if tool_call:
                tool_result = self.handle_tool_call(tool_call)
                self.conversation.append_observation(tool_result)
            else:
                self.conversation.append_user(self.prompter.get("continue"))
            self.conversation.next_round()

    def handle_tool_call(self, tool_call):
        # Base agent always passes tool calls to environment
        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            return parsed_call # Contains the ToolResult with error
        return self.environment.run_tool(parsed_call)

class PlannerAgent(BaseAgent):
    def __init__(self, environment, challenge, prompter):
        super().__init__(environment, challenge, prompter)

    def handle_tool_call(self, tool_call):
        # TODO see if delegating task
        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            return parsed_call # Contains the ToolResult with error

        # TODO call the tool and send back the result
