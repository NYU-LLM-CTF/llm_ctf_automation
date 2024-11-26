import time
from pathlib import Path
from nyuctf.challenge import CTFChallenge

from .conversation import Conversation, MessageRole, Message
from .tools import DelegateTool, FinishTaskTool

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

        self.running = True

    def run(self):
        while self.running:
            self.conversation.next_round()
            self.run_one_round()
            # Update end condition
            self.running = self.conversation.round <= self.max_rounds
    def run_one_round(self):
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

    def run_one_round(self):
        response, tool_call = self.backend.send(self.conversation.get_messages(len_observations=5))
        self.conversation.append_assistant(content=response, tool_data=tool_call)

        if tool_call:
            tool_result = self.handle_tool_call(tool_call)
            self.conversation.append_observation(tool_result)
        else:
            self.conversation.append_user(self.prompter.get("continue"))

    def handle_tool_call(self, tool_call):
        # pass tool calls to environment
        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            return parsed_call # Contains the ToolResult with error
        return self.environment.run_tool(parsed_call)


class PlannerAgent(BaseAgent):
    """The Planner Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)
        self.delegated_task = None

    def run_one_round(self):
        response, tool_call = self.backend.send(self.conversation.get_messages())
        self.conversation.append_assistant(content=response, tool_data=tool_call)

        if not tool_call:
            self.conversation.append_user(self.prompter.get("continue"))
            return

        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            # Contains the ToolResult with error
            self.conversation.append_observation(parsed_call)
            return

        if parsed_call.name == DelegateTool.NAME:
            self.delegated_task = parsed_call
            # MultiAgent system is responsible to add observation to the conversation.
        else:
            tool_result = self.environment.run_tool(parsed_call)
            self.conversation.append_observation(tool_result)

class ExecutorAgent(BaseAgent):
    """The Executor Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)
        self.max_rounds = 10

    def run_one_round(self):
        pass

class PlannerExecutorSystem:
    """Holds all the agents of the multi-agent system."""
    def __init__(self, environment, challenge, planner_prompter, planner_backend, executor_prompter, executor_backend):
        self.environment = environment
        self.challenge = challenge
        self.planner = PlannerAgent(environment, challenge, planner_prompter, planner_backend)
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
            self.planner.conversation.next_round()
            planner.run_one_round()

            if self.planner.delegated_task is not None:
                result = self.run_executor(self.planner.delegated_task)
                self.planner.conversation.append_observation(ToolResult.for_call(self.planner.delegated_task, result))
                planner.delegated_task = None
            
    def run_executor(self, task):
        executor = ExecutorAgent(self.environment, self.challenge, self.executor_prompter, self.executor_backend)
        self.all_executors.append(executor)

        while not executor.finished and executor.conversation.rounds <= executor.max_rounds:
            executor.conversation.next_round()
            executor.run_one_round()

        if executor.finish:
            # Send the executor finish summary to the planner.
            return executor.finish_summary
        else:
            # Executor did not complete the round, send empty result
            return self.executor_prompter.get("finish_empty")
