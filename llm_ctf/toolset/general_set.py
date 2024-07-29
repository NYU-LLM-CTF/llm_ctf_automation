from .tool_modules import *

class GiveUpException(Exception):
    pass

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
        status.debug_message(f"Starting client container {self.container_name}...")
        if self.volume:
            volumes = ['-v', f'{self.volume}:/home/ctfplayer/ctf_files']
        else:
            volumes = []
        if self.challenge.disable_docker:
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
        status.debug_message(f"Stopping client container {self.container_name}...")
        if self.challenge.disable_docker:
            return
        subprocess.run(['docker', 'stop', self.container_name], capture_output=True)

    @staticmethod
    def _clean(text):
        if text is None:
            return None
        return text.decode('utf-8', errors='backslashreplace').replace('\r\n', '\n')

    def run_cmd(self, command, timeout=4.0):
        """Run a command in the docker container and return
        {"stdout": stdout, "stderr": stderr, "returncode": returncode, "timed_out": timed_out}
        """
        if timeout is None: timeout = 4.0
        p = subprocess.Popen(
            ['docker', 'exec', self.container_name, 'bash', '-c', command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            # p = subprocess.run(
            #     ['docker', 'exec', self.container_name, 'bash', '-c', command],
            #     timeout=timeout, check=True, capture_output=True,
            # )
            stdout, stderr = p.communicate(timeout=timeout)
            out = self._clean(stdout)
            err = self._clean(stderr)
            # out = self._clean(p.stdout)
            # err = self._clean(p.stderr)
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
        super().__init__(challenge=challenge)
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

class GiveUp(Tool):
    NAME = "give_up"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__(challenge=challenge)
        self.challenge = challenge

    def __call__(self,
                 confirm: Annotated[bool,"a boolean flag to confirm that you want to give up"]):
        """Give up on the challenge"""
        if not confirm:
            return {"error": "You must confirm that you want to give up"}
        raise GiveUpException()
    
if __name__ == "__main__":
    pass