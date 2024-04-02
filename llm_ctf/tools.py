#!/usr/bin/env python3

# Tools for the model to use when solving CTF challenges.
# A few notes for adding new tools:
# - Each tool must be a subclass of Tool, and implement the __call__ method.
# - Each tool must include:
#     - A NAME field with the tool name.
#     - Type hints in the __call__ method with the parameters described using
#       an Annotated type
#     - The return type should NOT be annotated; the schemas used by OpenAI
#       don't describe the return type, so it's not necessary and the schema
#       generator will raise an error if you try to annotate it.
#     - A docstring for __call__ giving the overall description of the tool
#   These are used to automatically generate the schema for the tool.
# - Backends usually do some validation of the parameters provided by the model
#   before invoking the tool, but you should still be prepared to handle invalid
#   input in the __call__ method and return a nice error message.
# - Return values should be a JSON-serializable dictionary; if an error occurs,
#   then the only key should be "error" and the value should be a string.

import copy
import inspect
import json
import subprocess
import tempfile

from .utils import CALL_ID
from .ctflogging import status
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum

from typing import TYPE_CHECKING, Any, Optional, Set, get_type_hints
from typing_extensions import Annotated
if TYPE_CHECKING:
    from llm_ctf_solve import CTFChallenge
from tool_def_generator import ToolDefGenerator

SCRIPT_DIR = Path(__file__).parent.parent.resolve()
GHIDRA = SCRIPT_DIR / 'ghidra_11.0.1_PUBLIC/support/analyzeHeadless'

class CTFCategories(StrEnum):
    rev = "rev"
    pwn = "pwn"
    crypto = "crypto"
    misc = "misc"
    forensics = "forensics"
    web = "web"

# Some helpful classes for tool-related things
@dataclass
class ToolFunction:
    name: str
    """The name of the tool function"""
    arguments: Any
    """The unparsed arguments to the tool function"""
    parsed_arguments: Optional[dict[str,Any]]
    """The parsed arguments to the tool function"""

class ToolCall:
    def __init__(self, name, id, arguments=None, parsed_arguments=None):
        if id is None:
            id = CALL_ID()
        self.id = id
        self.function = ToolFunction(name, arguments, parsed_arguments)
        self.type = "function"

    def error(self, message):
        return ToolResult(self.name, self.id, {"error": message})

    @classmethod
    def create_unparsed(cls, name, id, arguments):
        """Create a ToolCall with arguments set."""
        return cls(name, id, arguments=arguments)

    @classmethod
    def create_parsed(cls, name, id, parsed_arguments):
        """Create a ToolCall with parsed_arguments set."""
        return cls(name, id, parsed_arguments=parsed_arguments)

    def parsed_copy(self, parsed_arguments) -> "ToolCall":
        """Returns a copy of this ToolCall with parsed_arguments set."""
        return ToolCall(
            self.name,
            self.id,
            arguments=copy.copy(self.function.arguments) if self.function.arguments else None,
            parsed_arguments=parsed_arguments
        )

    def __str__(self) -> str:
        if self.function.parsed_arguments:
            return f"{self.name}({self.function.parsed_arguments})"
        elif self.function.arguments:
            return f"{self.name}({self.function.arguments})"
        else:
            return f"{self.name}([arguments unset])"

    def __repr__(self) -> str:
        return f"<ToolCall {self.name=}, {self.id=}, {self.function=}>"

    @property
    def arguments(self):
        return self.function.arguments
    @arguments.setter
    def arguments(self, value):
        self.function.arguments = value

    @property
    def parsed_arguments(self):
        return self.function.parsed_arguments
    @parsed_arguments.setter
    def parsed_arguments(self, value):
        self.function.parsed_arguments = value

    def model_dump(self):
        # Serialize in OpenAI format
        if self.parsed_arguments is not None:
            args = json.dumps(self.parsed_arguments)
        else:
            # Trickier; could be anything
            try:
                args = json.dumps(self.arguments)
            except Exception as e:
                args = json.dumps(str(self.arguments))
        return {
            "id": self.id,
            "function": {
                "name": self.name,
                "arguments": args,
            },
            "type": self.type,
        }

    @property
    def name(self):
        return self.function.name



@dataclass
class ToolResult:
    name: str
    """The name of the tool that was run"""
    id: str
    """The ID of the tool call"""
    result: dict[str, Any]
    """The result of running the tool"""

    # Serialize in OpenAI format
    def model_dump(self):
        return dict(
            name=self.name,
            role="tool",
            content=json.dumps(self.result),
            tool_call_id=self.id,
        )
class AllCategories:
    """A class that can be used to indicate that a tool should be available in all categories."""
    pass

class Tool:
    # Attributes that must be set by subclasses
    NAME : str
    """The name of the tool as it should be displayed to the model"""
    CATEGORIES : Set[CTFCategories]|AllCategories = AllCategories
    """The categories in which the tool should be available"""

    # Automatically generated attributes
    schema : dict[str,Any]
    """The schema for the tool, generated from the __call__ method's annotations"""
    description : str
    """The description of the tool"""
    parameters : dict[str,Any]
    """The parameters of the tool"""
    required_parameters : set[str]
    """The required parameters of the tool"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.name = cls.NAME
        # Automatically generate the schema from the __call__ method's annotations
        generator = ToolDefGenerator(name_mappings=[(cls.__call__.__qualname__, cls.NAME)])
        cls.schema = generator.generate(cls.__call__)[0]
        # Some convenience attributes
        cls.description = cls.schema['function']['description']
        cls.required_parameters = set(cls.schema['function']['parameters']['required'])
        cls.parameters = {}
        hints = get_type_hints(cls.__call__)
        for p,v in inspect.signature(cls.__call__).parameters.items():
            if p == 'self': continue
            cls.parameters[p] = cls.schema['function']['parameters']['properties'][p].copy()
            cls.parameters[p]['name'] = p
            cls.parameters[p]['required'] = p in cls.schema['function']['parameters']['required']
            if v.default is not inspect.Parameter.empty:
                cls.parameters[p]['default'] = v.default
                cls.parameters[p]['required'] = False
            cls.parameters[p]['python_type'] = hints[p]

    def __init__(self, challenge: Optional["CTFChallenge"] = None):
        pass

    @classmethod
    def make_call(cls, id: Optional[str] = None, **kwargs) -> ToolCall:
        """Create a ToolCall for this tool, instantiating the function with the given arguments"""
        return ToolCall.create_parsed(cls.name, id, kwargs)

    def run(self, tc : ToolCall) -> ToolResult:
        """Run the tool on a parsed ToolCall, returning a ToolResult"""
        if tc.function.parsed_arguments is None:
            raise ValueError("ToolCall must have parsed_arguments set")
        result = self(**tc.function.parsed_arguments)
        return ToolResult(tc.name, tc.id, result)

    def __call__(self, **kwargs):
        """Implementation of the tool."""
        raise NotImplementedError

    def setup(self):
        """Set up the tool."""
        pass

    def teardown(self, exc_type, exc_value, traceback):
        """
        Tear down the tool.

        Called from __exit__ in the CTFChallenge context manager; if an
        exception occurred, exc_type, exc_value, and traceback will be set
        to the exception information.
        """
        pass

    def __repr__(self):
        return f"<Tool {self.name}>"

class CommandExec(Tool):
    NAME = "run_command"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
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
        if self.challenge.args.disable_docker:
            return
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
        if self.challenge.args.disable_docker:
            return
        subprocess.run(['docker', 'stop', self.container_name], capture_output=True)

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def run_cmd(self, command, timeout=10.0):
        """Run a command in the docker container and return
        {"stdout": stdout, "stderr": stderr, "returncode": returncode, "timed_out": timed_out}
        """
        if timeout is None: timeout = 10.0
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

    def __call__(self, command: Annotated[str, "the command to run"],
                       timeout: Annotated[float, "the maximum number of seconds to run the command"] = 10.0):
        """Execute a command in an Ubuntu container (persistent across calls)"""
        if command is None:
            return {"error": "No command provided"}
        return self.run_cmd(command, timeout)

class CheckFlag(Tool):
    NAME = "check_flag"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge
        self.real_flag = challenge.real_flag

    def __call__(self, flag: Annotated[str,"the flag to check"]):
        """Check if a flag is correct."""
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

class CreateFile(Tool):
    NAME = "createfile"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge
        self.container_name = challenge.container_name

    def __call__(self,
                 path: Annotated[str,"path where the file should be created; relative paths will be relative to /home/ctfplayer/"],
                 contents: Annotated[str,"contents of the file"],
                 decode_escapes: Annotated[bool,"whether to decode escape sequences in the contents"] = False):
        """Create a file in the container with the given contents"""
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

class Decompile(Tool):
    NAME = "decompile_function"
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn}
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge
        self._decomp_cache = {}

    def __call__(self,
                 path: Annotated[str,"path to the binary to decompile"],
                 function: Annotated[str,"the function to decompile"] = 'main'):
        """Decompile a function from a binary using Ghidra."""
        if path is None:
            return {"error": "No binary provided"}
        if function is None:
            function = "main"
        return self.decompile(path, function)

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

class Disassemble(Tool):
    NAME = "disassemble_function"
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn}
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge
        self._disasm_cache = {}

    def __call__(self,
                 path: Annotated[str,"path to the binary to disassemble"],
                 function: Annotated[str,"the function to disassemble"] = 'main'):
        """Disassemble a function from a binary using Ghidra."""
        if function is None:
            function = "main"
        if path is None:
            return {"error": "No binary provided"}
        return self.disassemble(path, function)

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

class GiveUpException(Exception):
    pass

class GiveUp(Tool):
    NAME = "give_up"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge

    def __call__(self,
                 confirm: Annotated[bool,"a boolean flag to confirm that you want to give up"]):
        """Give up on the challenge"""
        if not confirm:
            return {"error": "You must confirm that you want to give up"}
        raise GiveUpException()


# Predefined sets of tools for different categories; this is
# generated automatically based on the CATEGORIES attribute of each tool
DEFAULT_TOOLSET = Tool.__subclasses__()
categories = { "rev", "pwn", "crypto", "misc", "forensics", "web" }
TOOLSETS = {
    cat : [ t for t in DEFAULT_TOOLSET if t.CATEGORIES is AllCategories or cat in t.CATEGORIES ]
    for cat in CTFCategories
}
TOOLSETS["default"] = DEFAULT_TOOLSET

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
