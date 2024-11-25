import subprocess

from .tool import Tool, ToolResult

class RunCommandTool(Tool):
    NAME = "run_command"
    DESCRIPTION = "Run a shell command in the Docker container. Returns stdout, stderr, returncode, and timed_out."
    PARAMETERS = {
        "command": ("string", "the command to run"),
        "timeout": ("number", "timeout in seconds (default 10)")
    }
    REQUIRED_PARAMETERS = {"command"}

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def call(self, command=None, timeout=10.0):
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
