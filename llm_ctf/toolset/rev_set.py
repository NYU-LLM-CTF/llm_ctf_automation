from .tool_modules import *

SCRIPT_DIR = Path(__file__).parent.parent.resolve()
GHIDRA = SCRIPT_DIR / 'ghidra_11.0.1_PUBLIC/support/analyzeHeadless'

class Decompile(Tool):
    NAME = "decompile_function"
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn}
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.CATEGORIES = {"rev"}
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
            decomp_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.decomp.json"
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
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
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
    CATEGORIES = {CTFCategories.rev, CTFCategories.pwn}
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.CATEGORIES = {"rev"}
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
        disasm_output = SCRIPT_DIR / f"decomp/{self.challenge.category}/{self.challenge.chaldir.name}/{basename}.disas.json"

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
        binary_paths = self.challenge.chaldir.glob(f'**/{binary}')
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