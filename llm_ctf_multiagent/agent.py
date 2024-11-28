import time
from pathlib import Path
from nyuctf.challenge import CTFChallenge

from .logging import status
from .conversation import Conversation, MessageRole, Message
from .tools import DelegateTool, FinishTaskTool, ToolResult

now = lambda: time.time()

class BaseAgent:
    """Base class for an Agent"""
    def __init__(self, environment, challenge, prompter, backend):
        self.environment = environment
        self.challenge = challenge
        self.prompter = prompter
        self.backend = backend

        self.conversation = Conversation()
        self.max_rounds = 10
        self.running = True

    def run(self):
        """
        Basic loop to run the agent for fixed number of rounds.
        Calls run_one_round() for each iteration.
        """
        while self.running:
            self.conversation.next_round()
            self.run_one_round()
            # Update end condition
            self.running = self.conversation.round <= self.max_rounds

    def add_start_prompts(self):
        """
        Adds the system and initial prompts to the conversation.
        This is a separate function to allow adding more params to the prompts.
        """
        self.add_system_message(self.prompter.get("system"))
        self.add_user_message(self.prompter.get("initial"))

    # Helper functions to add and print messages to the conversation
    def add_system_message(self, message):
        self.conversation.append_system(message)
        status.system_message(message)
    def add_user_message(self, message):
        self.conversation.append_user(message)
        status.user_message(message)
    def add_assistant_message(self, message, tool_call):
        self.conversation.append_assistant(content=message, tool_data=tool_call)
        # Only print thought, action is printed after tool_call is parsed
        status.assistant_thought(message)
    def add_observation_message(self, tool_result):
        self.conversation.append_observation(tool_data=tool_result)
        status.observation_message(tool_result.result)

    def run_one_round(self):
        raise NotImplementedError


class SingleAgent(BaseAgent):
    """Original single agent implementation"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)
        self.add_start_prompts() # Don't need anything special for prompting.

    def __enter__(self):
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
        self.add_assistant_message(response, tool_call)

        if tool_call:
            tool_result = self.handle_tool_call(tool_call)
            self.add_observation_message(tool_result)
        else:
            self.add_user_message(self.prompter.get("continue"))

    def handle_tool_call(self, tool_call):
        # TODO remove this function
        # pass tool calls to environment
        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            # Print unparsed tool_call
            status.assistant_action(tool_call.formatted())
            return parsed_call # Contains the ToolResult with error
        # Print parsed tool_call
        status.assistant_action(parsed_call.formatted())
        return self.environment.run_tool(parsed_call)


class PlannerAgent(BaseAgent):
    """The Planner Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)
        self.delegated_task = None
        self.add_start_prompts()

    def run_one_round(self):
        response, tool_call = self.backend.send(self.conversation.get_messages())
        self.add_assistant_message(response, tool_call)

        if not tool_call:
            self.add_user_message(self.prompter.get("continue"))
            return

        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            # Print unparsed tool_call
            status.assistant_action(tool_call.formatted())
            # Contains the ToolResult with error
            self.add_observation_message(parsed_call)
            return

        # Print parsed tool_call
        status.assistant_action(parsed_call.formatted())

        if parsed_call.name == DelegateTool.NAME:
            self.delegated_task = parsed_call
            # MultiAgent system is responsible to add observation to the conversation.
        else:
            tool_result = self.environment.run_tool(parsed_call)
            self.add_observation_message(tool_result)

class ExecutorAgent(BaseAgent):
    """The Executor Agent of a multi-agent Planner-Executor system"""
    def __init__(self, environment, challenge, prompter, backend):
        super().__init__(environment, challenge, prompter, backend)
        self.max_rounds = 10
        self.finished = False
        self.finish_summary = None

    def run_one_round(self):
        response, tool_call = self.backend.send(self.conversation.get_messages())
        self.add_assistant_message(response, tool_call)

        if not tool_call:
            self.add_user_message(self.prompter.get("continue"))
            return

        parsed, parsed_call = self.backend.parse_tool_arguments(tool_call)
        if not parsed:
            # Print unparsed tool_call
            status.assistant_action(tool_call.formatted())
            # Contains the ToolResult with error
            self.add_observation_message(parsed_call)
            return
        # Print parsed tool_call
        status.assistant_action(parsed_call.formatted())

        if parsed_call.name == FinishTaskTool.NAME:
            # TODO Maybe have the agent retry if summary is empty?
            self.finish_summary = parsed_call.parsed_arguments.get("summary", None)
            self.finished = True
            # Executor is done here.
        else:
            tool_result = self.environment.run_tool(parsed_call)
            self.add_observation_message(tool_result)

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
                self.planner.conversation.round <= self.planner.max_rounds:
            self.planner.conversation.next_round()
            self.planner.run_one_round()

            if self.planner.delegated_task is not None:
                result = self.run_executor(self.planner.delegated_task)
                self.planner.add_observation_message(ToolResult.for_call(self.planner.delegated_task, result))
                self.planner.delegated_task = None
            
    def run_executor(self, task):
        status.print("============= EXECUTOR ==============", style="bold")
        executor = ExecutorAgent(self.environment, self.challenge, self.executor_prompter, self.executor_backend)
        self.all_executors.append(executor)

        # Add executor prompts
        task_description = task.parsed_arguments["task"]
        executor.add_system_message(executor.prompter.get("system"))
        executor.add_user_message(executor.prompter.get("initial", task_description=task_description))

        while not executor.finished and executor.conversation.round <= executor.max_rounds:
            executor.conversation.next_round()
            executor.run_one_round()

        status.print("============= EXECUTOR DONE =========", style="bold")
        if executor.finished and executor.finish_summary is not None:
            # Send the executor finish summary to the planner.
            return executor.finish_summary
        else:
            # Executor did not complete the round, send empty result
            return self.executor_prompter.get("finish_empty")
