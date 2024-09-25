from functools import cached_property
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from typing import List
import yaml
from .utilities.dockertool import DockerClient

from pathlib import Path
from .ctflogging import status

category_friendly = {
    "rev": "reverse engineering",
    "pwn": "binary exploitation",
    "web": "web security",
    "crypto": "cryptography",
    "misc": "miscellaneous",
    "forensics": "forensics",
}

category_short = {
    "crypto": "cry",
    "forensics": "for",
    "misc": "msc",
    "pwn": "pwn",
    "rev": "rev",
    "web": "web",
}

_rep_underscore = re.compile(r'_+')
def safe_name(s: str) -> str:
    """Create a safe name (suitable for docker) from a string
    """
    # Replace all non-alphanumeric characters with underscores
    safe = s.replace(' ', '_').lower()
    safe = ''.join(c if c.isalnum() else '_' for c in safe).rstrip('_')
    safe = _rep_underscore.sub('_', safe)
    return safe

def get_canonical_name(chaldir : Path|str) -> str:
    """Create a safe image name from a challenge; this is the same scheme
    that was used by the builder script to create the image name, so it
    can be used to predict the OCI name.
    """
    chaldir = Path(chaldir).resolve()
    year, event, category, name = chaldir.parts[-4:]

    chal_name = safe_name(name)
    event = event.rsplit('-',1)[1]
    event_char = event.lower()[0]
    cat = category_short[category]
    return f"{year}{event_char}-{cat}-{chal_name}"

def get_asi_name(chaldir : Path|str) -> str:
    return "asibench_" + get_canonical_name(chaldir)

# Helper so that we can format the challenge description without worrying about
# missing keys from accidental use of braces in the description
class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

class CTFEnvironment:
    def __init__(self, challenge_json: Path|str, args=None):
        self.args = args.__dict__ if args else {}
        self.disable_docker = self.args.get("disable_docker", False)
        # self.docker = DockerClient()
        self.challenge_json = Path(challenge_json)

        # Docker container information
        self.network = self.args.get("network", "ctfnet")
        self.tmpdir = None

        # Load challenge details from JSON
        self.load_challenge(self.challenge_json)

        # Client container information (FIXME: this shouldn't really live here)
        self.container_name = self.args.get("container_name", "ctfenv")
        self.container_image = self.args.get("container_image", "ctfenv")
        # Challenge server information
        self.challenge_server_proc = None
        self.challenge_server_log = None
        self.challenge_server_output = None

        # Gets set to true once the challenge is solved, either because check_flag()
        # detected the flag in the output or because the CheckFlag tool was called
        # with the correct flag
        self.solved = False

    def load_challenge(self, challenge_json : Path):
        # Load in all the challenge information from the challenge.json file
        self.challenge_json = challenge_json
        self.challenge = json.loads(challenge_json.read_text())
        # import pdb; pdb.set_trace()
        self.name = self.challenge.get("name", "UNKNOWN")
        self.is_compose = False
        self.has_files = "files" in self.challenge and self.challenge["files"]
        self.category = challenge_json.parent.parent.name
        self.category_friendly = category_friendly.get(self.category, self.category)
        self.chaldir = challenge_json.parent

        self.points = self.challenge.get("points", self.challenge.get("initial", 0))
        self.real_flag = self.challenge["flag"] if isinstance(self.challenge["flag"], str) else self.challenge['flag']['content']
        if '{' not in self.real_flag:
            status.debug_message(f"Flag for challenge {self.asiname} does not follow a standard format, please check!")
            self.flag_format = "not provided"
        else:
            self.flag_format = re.sub(r'\{.*?\}', '{...}', self.real_flag)
        assert self.flag_format != self.real_flag, f"Flag format for {self.asiname} would leak the flag!"
        self.challenge_port = self.challenge.get("internal_port")
        self.server_description = self.challenge.get("server_description")

        # Load any container images needed for the challenge. There are three cases:
        # 1. The challenge does not need a server. In this case, we don't need to load any images.
        # 2. The challenge uses a single container image. There will be a tar file in the challenge directory
        #    named self.canonical_oci_archive. The container name will be either self.canonical_name or
        #    self.asiname; if neither image is already loaded in docker, then load the .tar file.
        # 3. The challenge uses a docker-compose file. In this case, the challenge directory will contain multiple
        #    tar files, one for each service in the docker-compose file. The OCI filenames will be
        #    {self.canonical_name}-{service_name}.tar and the container names will be {self.asiname}-{service_name}.
        #    If any of the images are not already loaded in docker, then load the .tar files.
        # This will get a lot simpler once we are pushing iamges to Docker Hub, since we can just try to do
        # docker compose up or docker run and let it pull any images needed.
        # TODO: where should we get the server name from for the compose case?
        if not self.is_compose and len(self.oci_images) == 1:
            self.challenge_container = safe_name(self.fsname)
        elif 'box' in self.challenge:
            self.challenge_container = self.challenge['box']
        else:
            self.challenge_container = None
        self.server_type = self.get_server_type()
        self.files = self.challenge.get("files", [])

        # If the chal description contains {box} or {port} but we don't have
        # an image name, raise an error
        if '{box}' in self.challenge['description'] and not self.challenge_server_name:
            raise RuntimeError(f"Challenge {self.name} has placeholder for {{box}} in the description but no server name found")
        if '{port}' in self.challenge['description'] and not self.challenge_port:
            raise RuntimeError(f"Challenge {self.name} has placeholder for {{port}} in the description but no internal_port found")

    @property
    def description(self):
        return self.challenge['description'].format_map(
            SafeDict(box=self.challenge_server_name, port=self.challenge_port)
        )

    @property
    def challenge_server_name(self):
        if self.challenge_container:
            box = self.challenge_container
        elif 'box' in self.challenge:
            box = self.challenge['box']
        else:
            box = None
        return box

    def get_server_type(self):
        # TODO: simplify this / make it consistent
        if not self.challenge_server_name or not self.challenge_port:
            return None
        if self.category == "web" or self.category == "misc" and self.challenge.get("proto") != "nc":
            return "web"
        else:
            return "nc"

    def get_server_description(self):
        status.debug_message(self.challenge_container)
        status.debug_message(self.challenge_server_name)
        if self.challenge.get("server_description", None) is not None:
            return self.challenge["server_description"]
        # NB: Docker compose challenges are expected to have all the information
        # included in the description from challenge.json
        # TODO: simplify this / make it consistent
        if self.challenge_server_name:
            if self.category == "web" or self.category == "misc" and self.challenge.get("proto") != "nc":
                return f"The challenge web server is running on `{self.challenge_server_name}` port `{self.challenge_port}` and you can access it from within the container environment using `curl http://{self.challenge_server_name}:{self.challenge_port}`.\n\n"
            else:
                return f"The challenge server is running on `{self.challenge_server_name}` port `{self.challenge_port}` and you can access it from within the container environment using `nc {self.challenge_server_name} {self.challenge_port}`.\n\n"
        else:
            return ""

    def get_server_logs(self):
        if self.disable_docker:
            return None
        if self.is_compose:
            return self.get_compose_logs()
        if not self.challenge_server_log:
            return None
        self.challenge_server_log.flush()
        self.challenge_server_log.seek(0)
        return self.challenge_server_log.read().decode('utf-8', errors='replace')

    def get_compose_logs(self):
        return subprocess.check_output(
            ['docker', 'compose', '-f', self.chaldir / 'docker-compose.yml', 'logs'],
            text=True,
        )

    def start_challenge_container(self):
        if self.disable_docker:
            return
        
        for entry in os.scandir(self.chaldir):
            if entry.is_file() and entry.name == 'docker-compose.yml':
                self.is_compose = True

        if self.is_compose:
            status.debug_message(f"Starting challenge services with docker-compose")
            subprocess.run(
                ['docker', 'compose', '-f', self.chaldir / 'docker-compose.yml', 'up', '-d', '--force-recreate'],
                check=True, capture_output=True,
            )
            return

    def stop_challenge_container(self):
        if self.disable_docker:
            return
        if self.is_compose:
            status.debug_message(f"Stopping challenge services with docker-compose")
            self.challenge_server_output = self.get_server_logs()
            subprocess.run(
                ['docker', 'compose', '-f', self.chaldir / 'docker-compose.yml', 'down', '--rmi', 'local', '--volumes'],
                check=True, capture_output=True,
            )
            return

    def __enter__(self):
        # If there are files, copy them into a temporary directory
        if self.has_files:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.tmpdir = self._tmpdir.__enter__()
            # Set full permissions on the tmp folder for access inside the docker.
            os.chmod(self.tmpdir, 0o777)
            for filename in self.challenge["files"]:
                src = (self.chaldir / filename).resolve()
                dst = Path(self.tmpdir) / filename
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        # self.load_challenge_images()
        self.start_challenge_container()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_challenge_container()
        if self.tmpdir:
            self._tmpdir.__exit__(exc_type, exc_value, traceback)

    @cached_property
    def canonical_name(self) -> str:
        """Create a safe image name from a challenge; this is the same scheme
        that was used by the builder script to create the image name, so it
        can be used to predict the OCI name.
        """
        return get_canonical_name(self.chaldir)

    @cached_property
    def asiname(self) -> str:
        return "asibench_" + self.canonical_name

    @cached_property
    def _parts(self):
        return self.challenge_json.resolve().parts[-5:-1]

    @cached_property
    def year(self) -> int:
        return int(self._parts[0])

    @cached_property
    def event(self) -> str:
        return self._parts[1].split('-')[1]

    @cached_property
    def fsname(self) -> str:
        return self._parts[3]

    @cached_property
    def short_category(self) -> str:
        return category_short[self.category]
