from functools import cached_property
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import yaml
from .utilities.dockertool import DockerClient

from nyuctf.challenge import CTFChallenge
from pathlib import Path

class CTFEnvironment:
    def __init__(self, challenge: CTFChallenge, args=None):
        self.args = args.__dict__ if args else {}
        self.disable_docker = self.args.get("disable_docker", False)

        # Docker container information
        self.network = self.args.get("network", "ctfnet")
        self.tmpdir = None
        self.challenge = challenge

        # Client container information (FIXME: this shouldn't really live here)
        self.container_name = self.args.get("container_name", "ctfenv")
        self.container_image = self.args.get("container_image", "ctfenv")

    def __enter__(self):
        # If there are files, copy them into a temporary directory
        if self.challenge.has_files:
            self._tmpdir = tempfile.TemporaryDirectory()
            self.tmpdir = self._tmpdir.__enter__()
            # Set full permissions on the tmp folder for access inside the docker.
            os.chmod(self.tmpdir, 0o777)
            for filename in self.challenge.files:
                src = (self.challenge.challenge_dir / filename).resolve()
                dst = Path(self.tmpdir) / filename
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        self.challenge.start_challenge_container()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.challenge.stop_challenge_container()
        if self.tmpdir:
            self._tmpdir.__exit__(exc_type, exc_value, traceback)
