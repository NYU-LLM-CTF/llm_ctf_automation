import json
import os
import re
import shutil
import subprocess
import tempfile
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

# Helper so that we can format the challenge description without worrying about
# missing keys from accidental use of braces in the description
class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

class CTFChallenge:
    def __init__(self, challenge_json, args):
        self.args = args
        self.docker = DockerClient()
        self.load_challenge(Path(challenge_json))

        # Docker container information
        self.container_image = args.container_image
        self.container_name = args.container_name
        self.network = args.network
        self.is_compose = self.challenge.get("compose", False)
        self.tmpdir = None
        self.has_files = "files" in self.challenge and self.challenge["files"]
        # Gets set to true once the challenge is solved, either because check_flag()
        # detected the flag in the output or because the CheckFlag tool was called
        # with the correct flag
        self.solved = False

    def load_challenge(self, challenge_json):
        # Load in all the challenge information from the challenge.json file
        self.challenge_json = challenge_json
        self.category = challenge_json.parent.parent.name
        self.category_friendly = category_friendly.get(self.category, self.category)
        self.chaldir = challenge_json.parent
        self.challenge = json.loads(challenge_json.read_text())
        self.points = self.challenge.get("points", self.challenge.get("initial", 0))
        self.name = self.challenge["name"]
        self.real_flag = self.challenge["flag"] if isinstance(self.challenge["flag"], str) else self.challenge['flag']['content']
        self.flag_format = re.sub(r'\{.*?\}', '{...}', self.real_flag)
        self.challenge_port = self.challenge.get("internal_port")
        self.server_description = self.challenge.get("server_description")
        self.image_name = self.parse_oci_path()
        self.oci_info = self.parse_oci_container()
        self.oci_container = None if not self.oci_info else self.oci_info[-1]
        self.oci_fullname = None if not self.oci_info else "-".join(self.oci_info)
        self.asi_oci_fullname = None if not self.oci_info else "asibench_" + self.oci_fullname
        self.real_oci = self.oci_container
        self.challenge_container = self.challenge.get("container_image", self.oci_container)
        self.server_type = self.get_server_type()
        self.files = self.challenge.get("files", [])

    @property
    def description(self):
        return self.challenge['description'].format_map(
            SafeDict(box=self.challenge_container, port=self.challenge_port)
        )

    def load_challenge_image(self):
        if self.image_name:
            # image_list = subprocess.run(['docker', 'images'], stdout=subprocess.PIPE, text=True)
            image_list = self.docker.get_images()
            if self.oci_container not in image_list \
                and self.oci_fullname not in image_list \
                    and self.asi_oci_fullname not in image_list:
                status.debug_message(f"Load pre-build docker image {self.image_name.name}...")
                with open(self.image_name, 'rb') as oci:
                    subprocess.run(['docker', 'load'], stdin=oci)
                image_list = subprocess.run(['docker', 'images'], stdout=subprocess.PIPE, text=True)
                return
            status.debug_message(f"No pre-build docker image {self.image_name.name} found!")

    def parse_oci_container(self):
        if self.image_name:
            oci_parts =  self.image_name.stem.split('-', maxsplit=2)
            if len(oci_parts) != 3:
                status.debug_message(f"wrong oci image name format, correct name should be: year[q/f]-category-chalname")
                return None
            return oci_parts
        status.debug_message(f"No oci image found, skip")
        return None

    def parse_oci_path(self):
        if self.chaldir.is_dir():
            pattern = '[0-9][0-9][0-9][0-9][qf]-*.tar'
            matching_files = sorted(self.chaldir.glob(pattern))
        return matching_files[-1] if len(matching_files) > 0 else None

    def get_server_type(self):
        # TODO: simplify this / make it consistent
        if not self.challenge_container and not self.oci_container:
            return None
        if self.category == "web" or self.category == "misc" and self.challenge.get("proto") != "nc":
            return "web"
        else:
            return "nc"

    def get_server_description(self):
        if self.challenge.get("server_description", None) is not None:
            return self.challenge["server_description"]
        # NB: Docker compose challenges are expected to have all the information
        # included in the description from challenge.json
        # TODO: simplify this / make it consistent
        if self.challenge_container:
            if self.category == "web" or self.category == "misc" and self.challenge.get("proto") != "nc":
                return f"The challenge web server is running on `{self.challenge_container}` port `{self.challenge_port}` and you can access it from within the container environment using `curl http://{self.challenge_container}:{self.challenge_port}`.\n\n"
            else:
                return f"The challenge server is running on `{self.challenge_container}` port `{self.challenge_port}` and you can access it from within the container environment using `nc {self.challenge_container} {self.challenge_port}`.\n\n"
        else:
            return ""

    def start_challenge_container(self):
        if self.args.disable_docker:
            return

        if self.is_compose:
            status.debug_message(f"Starting challenge services with docker-compose")
            subprocess.run(
                ['docker', 'compose', '-f', self.chaldir / 'docker-compose.yml', 'up', '-d'],
                check=True, capture_output=True,
            )
            return
        # if not self.challenge_container: return
        if not self.oci_container and not self.challenge_container: return
        status.debug_message(f"Starting challenge container {self.oci_container}")
        image_list = self.docker.get_images()
        if self.real_oci not in image_list:
            self.real_oci = self.oci_fullname
        if self.real_oci not in image_list:
            self.real_oci = self.asi_oci_fullname
        subprocess.run(
            ['docker', 'run'] + \
            ['--network', self.network] + \
            ['--platform', 'linux/amd64', '-d', '--rm'] + \
            ['--name', self.challenge_container, self.real_oci],
            check=True, capture_output=True
        )
        # subprocess.run(
        #     ['docker', 'run'] + \
        #     ['--network', self.network] + \
        #     ['--platform', 'linux/amd64', '-d', '--rm'] + \
        #     ['--name', self.challenge_container, self.challenge_container],
        #     check=True, capture_output=True,
        # )

    def stop_challenge_container(self):
        if self.args.disable_docker:
            return
        if self.is_compose:
            status.debug_message(f"Stopping challenge services with docker-compose")
            subprocess.run(
                ['docker', 'compose', '-f', self.chaldir / 'docker-compose.yml', 'down'],
                check=True, capture_output=True,
            )
            return
        if not self.challenge_container: return
        status.debug_message(f"Stopping challenge container {self.challenge_container}")
        subprocess.run(
            ['docker', 'stop', self.challenge_container],
            check=True, capture_output=True,
        )

    def check_flag(self, resp):
        # Check if the flag is in the response; also check version with
        # escaped underscores because the model is writing Markdown and
        # sometimes gets over-eager about escaping things. Would be nice
        # to properly unescape the response with a Markdown parser but
        # apparently that's more difficult than it should be.
        unescaped_resp = resp.replace('\\_','_')
        if self.real_flag in resp or self.real_flag in unescaped_resp:
            status.print(
                f"\n[red bold]Correct flag found in the output:[/red bold] [green]{self.real_flag}[/green]",
                markup=True)
            self.solved = True
            return True
        else:
            return False

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
        self.load_challenge_image()
        self.start_challenge_container()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_challenge_container()
        if self.tmpdir:
            self._tmpdir.__exit__(exc_type, exc_value, traceback)
        if self.real_oci:
            # BDG: I'm not sure why we need this instead of just docker stop [container_name] ?
            command = f"docker ps --filter name={self.challenge_container} -q | xargs -r docker stop"
            subprocess.run(command, shell=True, check=True)
            # BDG: Ideally we would not remove the container image, but the server is
            # low on space
            subprocess.run(
                ['docker', 'rmi', self.real_oci]
            )
