import subprocess
import json
import re
import tempfile
from pathlib import Path
from typing_extensions import Annotated

from .modules import Tool, CTFCategories
from ..ctflogging import status

SCRIPT_DIR = Path(__file__).parent.parent.parent.resolve()
GHIDRA = SCRIPT_DIR / "ghidra_11.0.1_PUBLIC/support/analyzeHeadless"

class CommandExec(Tool):
    NAME = "run_command"
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def run_cmd(self, command, timeout):
        """Run a command in the docker container and return
        {"stdout": stdout, "stderr": stderr, "returncode": returncode, "timed_out": timed_out}
        """
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

    def __call__(self, command: Annotated[str, "the command to run"],
                       timeout: Annotated[float, "the maximum number of seconds to run the command"] = 10.0):
        """Execute a command in an Ubuntu container (persistent across calls)"""
        if command is None:
            return {"error": "No command provided"}
        return self.run_cmd(command, timeout)

class CheckFlag(Tool):
    NAME = "check_flag"
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment
        self.real_flag = environment.challenge.flag

    def __call__(self, flag: Annotated[str,"the flag to check"]):
        """Check if a flag is correct."""
        if flag is None:
            return {"error": "No flag provided"}
        status.print(f"Checking flag:")
        status.print(f"  Provided: [blue]{flag}[/blue]", markup=True)
        status.print(f"    Actual: [green]{self.real_flag}[/green]", markup=True)
        if flag == self.real_flag:
            status.print(f"[red bold]Correct flag![/red bold]", markup=True)
            self.environment.solved = True
            return {"correct": True}
        else:
            status.print(f"[red bold]Incorrect flag.[/red bold]", markup=True)
            return {"correct": False}

class CreateFile(Tool):
    NAME = "createfile"
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment

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
    def _expanduser(path, home):
        """Expand ~ and ~user constructs in the given path"""
        strpath = str(path)
        if strpath.startswith('~'):
            strpath = strpath.replace('~', str(home), 1)
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
        path = Path(self._expanduser(path, self.environment.container_home))
        if not path.is_absolute():
            path = self.environment.container_home / path
        with tempfile.NamedTemporaryFile(mode="wb") as f:
            f.write(contents)
            f.flush()
            try:
                path = self.environment.copy_into_container(f.name, path)
                return {"success": True, "path": str(path)}
            except subprocess.CalledProcessError as e:
                return {"error": f"Error copying file into container: {e.stderr.decode('utf-8', errors='backslashreplace')}"}

class GiveUp(Tool):
    NAME = "give_up"
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment

    def __call__(self, confirm: Annotated[bool,"a boolean flag to confirm that you want to give up"]):
        """Give up on the challenge"""
        if not confirm:
            return {"error": "You must confirm that you want to give up"}
        self.environment.giveup = True
        return {"success": True}

class Decompile(Tool):
    NAME = "decompile_function"
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn, CTFCategories.crypto}
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment
        self.challenge = self.environment.challenge
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

    def find_function(self, dis, function):
        if function in dis["functions"]:
            return dis["functions"][function]
        # Looking for main entry point, so try other names also
        if function == "main":
            if "_start" in dis["functions"]:
                return dis["functions"]["_start"]
            if "invoke_main" in dis["functions"]:
                return dis["functions"]["invoke_main"]
        # Check if requesting radare2 unnamed function with address
        if re.match(r"fcn\.[0-9a-f]+$", function):
            addr = function[4:]
            if addr in dis["addresses"]:
                return dis["functions"][dis["addresses"][addr]]
        # Nothing found
        return None

    def decompile(self, binary, function):
        # Look for the decompilation output in "decomp"
        basename = Path(binary).name
        if basename not in self._decomp_cache:
            decomp_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.challenge_dir.name}/{basename}.decomp.json"
            if decomp_output.exists():
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())
            else:
                if not self.run_ghidra(basename, decomp_output):
                    return {"error": f"Decompilation for {binary} not available"}
                self._decomp_cache[basename] = json.loads(decomp_output.read_text())

        if found := self.find_function(self._decomp_cache[basename], function):
            return {"decompilation": found}
        else:
            return {"error": f"Function {function} not found in {binary}"}

    def run_ghidra(self, binary, output):
        status.debug_message(f"Running Ghidra to decompile {binary}...")
        binary_paths = self.challenge.challenge_dir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        status.debug_message(f"Real binary path: {real_binary}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'llm_ctf/ghidra_scripts',
                 "-import", real_binary, "-postscript", "DecompileToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()

class Disassemble(Tool):
    NAME = "disassemble_function"
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn, CTFCategories.crypto}
    def __init__(self, environment: "CTFEnvironment"):
        super().__init__()
        self.environment = environment
        self.challenge = self.environment.challenge
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

    def find_function(self, dis, function):
        if function in dis["functions"]:
            return dis["functions"][function]
        # Looking for main entry point, so try other names also
        if function == "main":
            if "_start" in dis["functions"]:
                return dis["functions"]["_start"]
            if "invoke_main" in dis["functions"]:
                return dis["functions"]["invoke_main"]
        # Check if requesting radare2 unnamed function with address
        if re.match(r"fcn\.[0-9a-f]+$", function):
            addr = function[4:]
            if addr in dis["addresses"]:
                return dis["functions"][dis["addresses"][addr]]
        # Nothing found
        return None

    def disassemble(self, binary, function):
        # Look for the disassembly output in "decomp"
        basename = Path(binary).name
        disasm_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.challenge_dir.name}/{basename}.disas.json"

        if basename not in self._disasm_cache:
            if disasm_output.exists():
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())
            else:
                if not self.run_ghidra(basename, disasm_output):
                    return {"error": f"Disassembly for {binary} not available"}
                self._disasm_cache[basename] = json.loads(disasm_output.read_text())

        if found := self.find_function(self._disasm_cache[basename], function):
            return {"disassembly": found}
        else:
            return {"error": f"Function {function} not found in {binary}"}

    def run_ghidra(self, binary, output):
        status.debug_message(f"Running Ghidra to disassemble {binary}...")
        binary_paths = self.challenge.challenge_dir.glob(f'**/{binary}')
        real_binary = next(binary_paths, None)
        if not real_binary or not real_binary.exists():
            return False
        status.debug_message(f"Real binary path: {real_binary}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subprocess.run(
                [GHIDRA, tmpdir, "DummyProj", "-scriptpath", SCRIPT_DIR / 'llm_ctf/ghidra_scripts',
                 "-import", real_binary, "-postscript", "DisassembleToJson.java", output],
                check=False, capture_output=True,
            )
            return output.exists()
