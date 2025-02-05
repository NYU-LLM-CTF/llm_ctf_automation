import subprocess

from ..logging import logger
from .tool import Tool, ToolResult

class RunCommandTool(Tool):
    NAME = "run_command"
    DESCRIPTION = "Run a shell command in the Docker container. Returns stdout, stderr, returncode, and timed_out."
    PARAMETERS = {
        "command": ("string", "the command to run"),
        "timeout": ("number", "timeout in seconds (default 300)")
    }
    REQUIRED_PARAMETERS = {"command"}

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        try:
            return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')
        except Exception as e:
            print(f"{type(text)} cannot be decoded, check the text format! \nTrack: {e}")
            return None

    def call(self, command=None, timeout=300.0):
        if command is None:
            return {"error": "No command provided"}

        p = subprocess.Popen(
            ['docker', 'exec', self.environment.container, 'bash', '-c', command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = p.communicate(timeout=timeout)
            out = self._clean(stdout)
            err = self._clean(stderr)
            return {"stdout": out, "stderr": err, "returncode": p.returncode, "timed_out": False}
        except subprocess.TimeoutExpired as e:
            p.kill()
            stdout, stderr = p.communicate(timeout=timeout)     
            out = self._clean(stdout)
            err = self._clean(stderr) 
            # out = self._clean(e.stdout)
            # err = self._clean(e.stderr)
            return {"stdout": out, "stderr": err, "returncode": None, "timed_out": True}
        except subprocess.CalledProcessError as e:
            out = self._clean(e.stdout)
            err = self._clean(e.stderr)
            return {"stdout": out, "stderr": err, "returncode": e.returncode, "timed_out": False}

    def print_tool_call(self, tool_call):
        logger.assistant_action(f"**{self.NAME}**\n```\n{tool_call.parsed_arguments['command']}\n```")
        
    def print_result(self, tool_result):
        if "error" in tool_result.result:
            logger.print(f"[bold]{self.NAME}[/bold]: [red]{tool_result.result['error']}[/red]", markup=True)
        else:
            logger.observation_message(f"**returncode**: {tool_result.result['returncode']} **timed out**: {tool_result.result['timed_out']}\n\n" +\
                    f"**stdout**:\n```\n{tool_result.result['stdout']}\n```\n\n" + \
                    f"**stderr**:\n```\n{tool_result.result['stderr']}\n```\n\n")

