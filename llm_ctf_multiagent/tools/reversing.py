from pathlib import Path
import json
import re
import subprocess

from .tool import Tool
from ..logging import status

DECOMPILE = "/opt/ghidra/customScripts/decompile.sh"
DISASSEMBLE = "/opt/ghidra/customScripts/disassemble.sh"

class GhidraBaseTool(Tool):
    """
    Base class for accessing Ghidra.
    Do not use this directly, only use the subclasses.
    """
    NAME = None
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.rev_cache = {}

    def find_function(self, dis, function):
        if function in dis["functions"]:
            return dis["functions"][function]
        # Looking for main entry point, so try other names also
        if function == "main":
            if "_start" in dis["functions"]:
                return dis["functions"]["_start"]
            if "invoke_main" in dis["functions"]:
                return dis["functions"]["invoke_main"]
            if "entry" in dis["functions"]:
                return dis["functions"]["entry"]
        # Check if requesting radare2 unnamed function with address
        if re.match(r"fcn\.[0-9a-f]+$", function):
            addr = function[4:]
            if addr in dis["addresses"]:
                return dis["functions"][dis["addresses"][addr]]
        # Nothing found
        return None

    def run_ghidra(self, script, binary):
        status.debug_message(f"Running Ghidra for {binary}...")
        # TODO add timeout
        res = subprocess.run(["docker", "exec", self.environment.container, script, binary],
                             check=False, capture_output=True)
        if res.returncode != 0:
            status.debug_message("GHIDRA FAILED!!")
            status.debug_message(res.stdout.decode("utf-8"))
            return None
        out = json.loads(res.stdout.decode("utf-8"))
        # status.debug_message("\n".join(out["functions"].keys()))
        return out

    def format_tool_call(self, tool_call):
        return f"**{self.NAME}** binary:`{tool_call.parsed_arguments['binary']}` function:`{tool_call.parsed_arguments['function']}`"

class DisassembleTool(GhidraBaseTool):
    NAME = "disassemble"
    DESCRIPTION = "Disassemble a function from a binary using Ghidra."
    PARAMETERS = {
        "binary": ("string", "path of the binary to disassemble"),
        "function": ("string", "function name to disassemble (default 'main')")
    }
    REQUIRED_PARAMETERS = {"binary"}

    def __init__(self, environment):
        super().__init__(environment)

    def call(self, binary=None, function="main"):
        """Disassemble a function from a binary using Ghidra."""
        if binary is None:
            return {"error": "No binary provided"}

        if binary not in self.rev_cache:
            disasm_out = self.run_ghidra(DISASSEMBLE, binary)
            if disasm_out is None:
                return {"error": f"Failed to run Ghidra for {binary}! Make sure the file exists and is a binary file."}
            self.rev_cache[binary] = disasm_out

        if found := self.find_function(self.rev_cache[binary], function):
            return {"disassembly": found}
        else:
            return {"error": f"Function {function} not found in {binary}"}

    def format_result(self, tool_result):
        if "error" in tool_result.result:
            return f"**{self.NAME}**: [red]{tool_result.result['error']}[/red]"
        else:
            return f"**{self.NAME}**\n```\n{tool_result.result['disassembly']}\n```"

class DecompileTool(GhidraBaseTool):
    NAME = "decompile"
    DESCRIPTION = "Decompile a function from a binary using Ghidra."
    PARAMETERS = {
        "binary": ("string", "path of the binary to decompile"),
        "function": ("string", "function name to decompile (default 'main')")
    }
    REQUIRED_PARAMETERS = {"binary"}

    def __init__(self, environment):
        super().__init__(environment)

    def call(self, binary=None, function="main"):
        """Decompile a function from a binary using Ghidra."""
        if binary is None:
            return {"error": "No binary provided"}

        if binary not in self.rev_cache:
            decomp_out = self.run_ghidra(DECOMPILE, binary)
            if decomp_out is None:
                return {"error": f"Failed to run Ghidra for {binary}! Make sure the file exists and is a binary file."}
            self.rev_cache[binary] = decomp_out

        if found := self.find_function(self.rev_cache[binary], function):
            return {"decompilation": found}
        else:
            return {"error": f"Function {function} not found in {binary}"}

    def format_result(self, tool_result):
        if "error" in tool_result.result:
            return f"**{self.NAME}**: [red]{tool_result.result['error']}[/red]"
        else:
            return f"**{self.NAME}**\n```\n{tool_result.result['decompilation']}\n```"
