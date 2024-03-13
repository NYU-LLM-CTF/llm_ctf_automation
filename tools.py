#!/usr/bin/env python3

import re
import json
import subprocess
import tempfile
from ctflogging import status
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from llm_ctf_solve import CTFChallenge

SCRIPT_DIR = Path(__file__).parent.resolve()
GHIDRA = SCRIPT_DIR / 'ghidra_11.0_PUBLIC/support/analyzeHeadless'

class Tool:
    def __init__(self, schema):
        self.schema = schema
        self.name = schema['function']['name']
        self.description = schema['function']['description']
        self.parameters = schema['function']['parameters']

    def extract_parameters(self, message):
        """Extract parameters from a message"""
        arguments = {}
        for param_name in self.parameters['properties']:
            arguments[param_name] = message.get(param_name)
        return arguments

    def run(self, message):
        """Run the tool on a message, returning a JSON string"""
        arguments = self.extract_parameters(message)
        result = self(**arguments)
        return json.dumps(result)

    def setup(self):
        """Setup the tool"""
        pass

    def __call__(self, **kwargs):
        """Implementation of the tool"""
        raise NotImplementedError

    def teardown(self, exc_type, exc_value, traceback):
        """Teardown the tool"""
        pass

    def __repr__(self):
        return f"<Tool {self.name}>"

COMMAND_EXEC_TOOL = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": "Execute a command in an Ubuntu container (persistent across calls)",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "the command to run",
                },
                "timeout": {
                    "type": "integer",
                    "description": "the maximum number of seconds to run the command (defaults to 10)",
                }
            },
            "required": ["command"],
        },
    },
}
class CommandExec(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(COMMAND_EXEC_TOOL)
        self.challenge = challenge
        self.container_image = challenge.container_image
        self.container_name = challenge.container_name
        self.network = challenge.network
        self.volume = challenge.tmpdir

    def setup(self):
        self.start_docker()

    def start_docker(self):
        status.debug_message("Starting docker container...")
        if self.volume:
            volumes = ['-v', f'{self.volume}:/home/ctfplayer/ctf_files']
        else:
            volumes = []
        subprocess.run(
            ['docker', 'run'] + \
                volumes + \
                ['--network', self.network] + \
                ['--platform', 'linux/amd64', '-d', '--rm'] + \
                ['--name', self.container_name, self.container_image],
            check=True, capture_output=True,
        )

    def teardown(self, exc_type, exc_value, traceback):
        # If there was an error, make a copy of the container for debugging
        if exc_type is not None:
            status.debug_message("Error detected; saving container for debugging...")
            subprocess.run(
                ['docker', 'commit', self.container_name, 'ctfenv_debug'],
            )
        self.stop_docker()

    def stop_docker(self):
        status.debug_message("Stopping docker container...")
        subprocess.run(['docker', 'stop', self.container_name], capture_output=True)

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def run_cmd(self, command, timeout=10):
        """Run a command in the docker container and return
        {"stdout": stdout, "stderr": stderr, "returncode": returncode, "timed_out": timed_out}
        """
        if timeout is None: timeout = 10
        status.debug_message(f"Running command with timeout={timeout}:\n{command}")
        try:
            p = subprocess.run(
                ['docker', 'exec', self.container_name, 'bash', '-c', command],
                timeout=timeout, check=True, capture_output=True,
            )
            out = self._clean(p.stdout)
            err = self._clean(p.stderr)
            return {"stdout": out, "stderr": err, "returncode": p.returncode, "timed_out": False}
        except subprocess.TimeoutExpired as e:
            out = self._clean(e.stdout)
            err = self._clean(e.stderr)
            return {"stdout": out, "stderr": err, "returncode": None, "timed_out": True}
        except subprocess.CalledProcessError as e:
            out = self._clean(e.stdout)
            err = self._clean(e.stderr)
            return {"stdout": out, "stderr": err, "returncode": e.returncode, "timed_out": False}

    def __call__(self, command, timeout=10):
        if command is None:
            return {"error": "No command provided"}
        return self.run_cmd(command, timeout)

CHECKFLAG_TOOL = {
    "type": "function",
    "function": {
        "name": "checkflag",
        "description": "Check if a flag is correct",
        "parameters": {
            "type": "object",
            "properties": {
                "flag": {
                    "type": "string",
                    "description": "the flag to check",
                },
            },
            "required": ["flag"],
        },
    },
}
class CheckFlag(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(CHECKFLAG_TOOL)
        self.challenge = challenge
        self.real_flag = challenge.real_flag

    def __call__(self, flag=None):
        if flag is None:
            return {"error": "No flag provided"}
        status.print(f"Checking flag:")
        status.print(f"  Provided: [blue]{flag}[/blue]", markup=True)
        status.print(f"    Actual: [green]{self.real_flag}[/green]", markup=True)
        if flag == self.real_flag:
            status.print(f"[red bold]Correct flag![/red bold]", markup=True)
            self.challenge.solved = True
            return {"correct": True}
        else:
            status.print(f"[red bold]Incorrect flag.[/red bold]", markup=True)
            return {"correct": False}

CREATEFILE_TOOL = {
    "type": "function",
    "function": {
        "name": "createfile",
        "description": "create a file in the container with the given contents",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "path where the file should be created; relative paths will be relative to /home/ctfplayer/",
                },
                "contents": {
                    "type": "string",
                    "description": "contents of the file",
                },
                "decode_escapes": {
                    "type": "boolean",
                    "description": "whether to decode escape sequences in the contents (defaults to False)",
                },
            },
            "required": ["path", "contents"],
        },
    },
}
class CreateFile(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(CREATEFILE_TOOL)
        self.challenge = challenge
        self.container_name = challenge.container_name

    def __call__(self, path=None, contents=None, decode_escapes=None):
        if path is None:
            return {"error": "No path provided"}
        if contents is None:
            return {"error": "No contents provided"}
        if decode_escapes is None:
            decode_escapes = False
        return self.createfile(path, contents)

    @staticmethod
    def _expanduser(path, home='/home/ctfplayer'):
        """Expand ~ and ~user constructs in the given path"""
        strpath = str(path)
        if strpath.startswith('~'):
            strpath = strpath.replace('~', home, 1)
        return Path(strpath)

    def createfile(self, path, contents, decode_escapes=False):
        if decode_escapes:
            # Decode escape sequences to get a bytes object
            try:
                contents = bytes(contents, 'utf-8').decode('unicode_escape').encode('latin-1')
            except UnicodeDecodeError as e:
                return {"error": f"Invalid escape sequence in contents: {e}"}
        else:
            contents = contents.encode()
        path = Path(path)
        path = self._expanduser(path)
        if not path.is_absolute():
            path = Path('/home/ctfplayer') / path
        path = str(path)
        with tempfile.NamedTemporaryFile(mode='wb') as f:
            f.write(contents)
            f.flush()
            tmpfile = f.name
            # Copy the file into the container
            try:
                subprocess.run(
                    ['docker', 'cp', tmpfile, f'{self.container_name}:{path}'],
                    check=True, capture_output=True,
                )
                # Set ownership to ctfplayer
                subprocess.run(
                    ['docker', 'exec', '--user=root', '-it', self.container_name, 'chown', 'ctfplayer:ctfplayer', path],
                    check=True, capture_output=True,
                )
                return {"success": True, "path": path}
            except subprocess.CalledProcessError as e:
                return {"error": f"Error copying file into container: {e.stderr.decode('utf-8', errors='backslashreplace')}"}

DECOMPILE_TOOL = {
    "type": "function",
    "function": {
        "name": "decompile_function",
        "description": "Decompile a function from a binary using Ghidra",
        "parameters": {
            "type": "object",
            "properties": {
                "binary": {
                    "type": "string",
                    "description": "the binary to decompile",
                },
                "function": {
                    "type": "string",
                    "description": "the function to decompile (defaults to main)",
                },
            },
            "required": ["binary", "function"],
        },
    },
}
class Decompile(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(DECOMPILE_TOOL)
        self.challenge = challenge
        self._decomp_cache = {}

    def __call__(self, binary=None, function=None):
        if binary is None:
            return {"error": "No binary provided"}
        if function is None:
            function = "main"
        return self.decompile(binary, function)

    def decompile(self, binary, function):
        # Look for the decompilation output in "decomp"
        basename = Path(binary).name
        if basename not in self._decomp_cache:
            self._decomp_cache[basename] = {}
            decomp_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.decomp.json"
            if decomp_output.exists():
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())
            else:
                if not self.run_ghidra(basename, decomp_output):
                    return {"error": f"Decompilation for {binary} not available"}
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())
        if function not in self._decomp_cache[basename]:
            # If they're trying to find main, try again with _start instead
            if function == "main":
                return self.decompile(binary, "_start")
            else:
                return {"error": f"Function {function} not found in {binary}"}
        return {"decompilation": self._decomp_cache[basename][function]}

    def run_ghidra(self, binary, output):
        status.debug_message(f"Running Ghidra to decompile {binary}...")
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        status.debug_message(f"Real binary path: {real_binary}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'ghidra_scripts',
                 "-import", real_binary, "-postscript", "DecompileToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()

DISASSEMBLE_TOOL = {
    "type": "function",
    "function": {
        "name": "disassemble_function",
        "description": "Disassemble a function from a binary using Ghidra",
        "parameters": {
            "type": "object",
            "properties": {
                "binary": {
                    "type": "string",
                    "description": "the binary to disassemble",
                },
                "function": {
                    "type": "string",
                    "description": "the function to disassemble (defaults to main)",
                },
            },
            "required": ["binary", "function"],
        },
    },
}

class GiveUpException(Exception):
    pass

class Disassemble(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(DISASSEMBLE_TOOL)
        self.challenge = challenge
        self._disasm_cache = {}

    def __call__(self, binary=None, function=None):
        if function is None:
            function = "main"
        if binary is None:
            return {"error": "No binary provided"}
        return self.disassemble(binary, function)

    def disassemble(self, binary, function):
        # Look for the disassembly output in "decomp"
        basename = Path(binary).name
        disasm_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.disas.json"

        if basename not in self._disasm_cache:
            if disasm_output.exists():
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())
            else:
                if not self.run_ghidra(basename, disasm_output):
                    return {"error": f"Disassembly for {binary} not available"}
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())

        if function not in self._disasm_cache[basename]:
            # If they're trying to find main, try again with _start instead
            if function == "main":
                return self.disassemble(binary, "_start")
            else:
                return {"error": f"Function {function} not found in {binary}"}
        return {"disassembly": self._disasm_cache[basename][function]}

    def run_ghidra(self, binary, output):
        status.debug_message(f"Running Ghidra to disassemble {binary}...")
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        status.debug_message(f"Real binary path: {real_binary}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'ghidra_scripts',
                 "-import", real_binary, "-postscript", "DisassembleToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()

class GiveUp(Tool):
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(GIVEUP_TOOL)
        self.challenge = challenge

    def __call__(self, confirm=None):
        if not confirm:
            return {"error": "You must confirm that you want to give up"}
        raise GiveUpException()

GIVEUP_TOOL = {
    "type": "function",
    "function": {
        "name": "give_up",
        "description": "Give up on the challenge",
        "parameters": {
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "a boolean flag to confirm that you want to give up",
                },
            },
            "required": ["confirm"],
        },
    },
}

DEFAULT_TOOLSET = [ CommandExec, CheckFlag, CreateFile, Decompile, Disassemble, GiveUp ]

# Predefined sets of tools for different categories
TOOLSETS = {
    # No binaries in the misc, forensics, or crypto categories
    "crypto": [ CommandExec, CheckFlag, CreateFile, GiveUp ],
    "misc": [ CommandExec, CheckFlag, CreateFile, GiveUp ],
    "forensics": [ CommandExec, CheckFlag, CreateFile, GiveUp ],
    "default": DEFAULT_TOOLSET,
}

if __name__ == "__main__":
    import sys
    from argparse import Namespace
    from llm_ctf_solve import CTFChallenge
    dis = Disassemble(
        CTFChallenge(Path(sys.argv[1]), Namespace(container_image="ubuntu:20.04"))
    )
    dis.disassemble(sys.argv[2], 'main')
    print('\n'.join(dis._disasm_cache[sys.argv[2]].keys()))

    dc = Decompile(
        CTFChallenge(Path(sys.argv[1]), Namespace(container_image="ubuntu:20.04"))
    )
    dc.decompile(sys.argv[2], 'main')
    print('\n'.join(dc._decomp_cache[sys.argv[2]].keys()))
