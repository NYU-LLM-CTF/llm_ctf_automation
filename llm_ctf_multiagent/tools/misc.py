from .tool import Tool

class SubmitFlagTool(Tool):
    NAME = "submit_flag"
    DESCRIPTION = "Submit the flag for the CTF challenge. If the flag is correct, the challenge ends with success, else this command returns error and you can continue with the challenge."
    PARAMETERS = {
        "flag": ("string", "the flag"),
    }
    REQUIRED_PARAMETERS = {"flag"}

    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.actual_flag = environment.challenge.flag

    def call(self, flag=None):
        if flag is None:
            return {"error": "Flag not provided!"}
        if flag != self.actual_flag:
            return {"error": "Flag is wrong!"}
        self.environment.solved = True
        return {"success": True}

class GiveupTool(Tool):
    # TODO maybe add back the confirm=true
    NAME = "giveup"
    DESCRIPTION = "Give up this challenge to terminate it immediately. Use this to stop solving the challenge."
    PARAMETERS = {}
    REQUIRED_PARAMETERS = set()

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    def call(self):
        self.environment.giveup = True
        return {"success": True}

class DelegateTool(Tool):
    """Tool to delegate task from planner to executor"""
    NAME = "delegate"
    DESCRIPTION = "Delegate a task to an executor LLM agent. The executor agent is fully autonomous and equipped with various tools for CTF challenges."
    PARAMETERS = {
        "task": ("string", "a detailed task description."),
    }
    REQUIRED_PARAMETERS = {"task"}
    def __init__(self, environment):
        super().__init__()
