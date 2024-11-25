import time
from pathlib import Path
from nyuctf.challenge import CTFChallenge

from .conversation import Conversation, MessageRole, Message

now = lambda: time.time()

class BaseAgent:
    """Base class for an Agent"""
    def __init__(self, environment, challenge, prompter, backend):
        self.environment = environment
        self.challenge = challenge
        self.prompter = prompter
        self.backend = backend

        # Start a conversation and inject system and initial prompts
        self.conversation = Conversation()
        self.conversation.append_system(self.prompter.get("system"))
        self.conversation.append_user(self.prompter.get("initial"))
        self.max_rounds = 5

    def run(self):
        raise NotImplementedError
    def handle_tool_call(self, tool_call):
        raise NotImplementedError

class SingleAgent(BaseAgent):
    """Original single agent implementation"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)

    def __enter__(self):
        # self.backend.setup() # TODO what setup does backend need?
        self.challenge.start_challenge_container()
        self.environment.setup()
        self.start_time = now()
        return self

    def __exit__(self, ex_type, ex_val, tb):
        self.environment.teardown(ex_type, ex_val, tb)
        self.challenge.stop_challenge_container()
        self.end_time = now()

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
        # pass tool calls to environment
        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            return parsed_call # Contains the ToolResult with error
        return self.environment.run_tool(parsed_call)


class PlannerAgent(BaseAgent):
    """The Planner Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend, multiagent):
        super().__init__(environment, challenge, prompter, backend)
        self.multiagent = multiagent

    def run(self):
        while self.conversation.round <= self.max_rounds:
            self.conversation.next_round()

            response, tool_call = self.backend.send(self.conversation.get_messages())
            self.conversation.append_assistant(content=response, tool_data=tool_call)

            if not tool_call:
                self.conversation.append_user(self.prompter.get("continue"))
                continue

            parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
            if not parsed:
                # Contains the ToolResult with error
                self.conversation.append_observation(parsed_call)
                continue

            if parsed_call.name == "delegate":
                print("DELEGATING TASK")
                print(parsed_call.parsed_arguments["task"])
                result = self.multiagent.delegate(parsed_call.parsed_arguments["task"])
                self.conversation.append_observation(ToolResult.for_call(parsed_call, result))
            else:
                tool_result = self.environment.run_tool(parsed_call)
                self.conversation.append_observation(tool_result)

class ExecutorAgent(BaseAgent):
    """The Executor Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend, multiagent):
        super().__init__(environment, challenge, prompter, backend)
        self.multiagent = multiagent
        self.max_rounds = 10

    def run(self):
        pass

class PlannerExecutorSystem:
    """Holds all the agents of the multi-agent system."""
    def __init__(self, environment, challenge, planner_prompter, planner_backend, executor_prompter, executor_backend):
        self.environment = environment
        self.challenge = challenge
        self.planner = PlannerAgent(environment, challenge, planner_prompter, planner_backend, self)
        self.executor_prompter = executor_prompter
        self.executor_backend = executor_backend

        self.all_executors = []

    def __enter__(self):
        self.challenge.start_challenge_container()
        self.environment.setup()
        self.start_time = now()
        return self

    def __exit__(self, ex_type, ex_val, tb):
        self.environment.teardown(ex_type, ex_val, tb)
        self.challenge.stop_challenge_container()
        self.end_time = now()

    def run(self):
        while not self.environment.solved and not self.environment.giveup and \
                self.planner.conversation.rounds <= self.planner.max_rounds:
            planner.run()
            
    def delegate(self, task):
        pass
