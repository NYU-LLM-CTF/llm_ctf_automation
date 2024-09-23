from datetime import datetime
import socket
import subprocess
import time
import json, os
import argparse
import shutil
import getpass
import yaml
from pathlib import Path

from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

from llm_ctf.ctflogging import status
from llm_ctf.backends import Backend
from llm_ctf.formatters import Formatter
from llm_ctf.prompts.prompts import PromptManager
from llm_ctf.environment import CTFEnvironment
from llm_ctf.conversation import CTFConversation

from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

def overwrite_args(args=None, config: dict=None):
    if not args or not config:
        return
    if "parameter" in config:
        args.max_rounds = config["parameter"].get("max_rounds", args.max_rounds)
        args.backend = config["parameter"].get("backend", args.backend)
        args.model = config["parameter"].get("model", args.model)
        args.max_cost = config["parameter"].get("max_cost", args.max_cost)
        args.experiment_name = config["experiment"].get("name", args.experiment_name)
        # TODO remove script_dir
        args.logdir = str(script_dir / "logs" / getpass.getuser() / f"{args.experiment_name}_round_{args.index}")
        args.debug = config["experiment"].get("debug", args.debug)
        args.skip_exist = config["experiment"].get("skip_exist", args.skip_exist)

def load_config(args=None):
    if args.config:
        try:
            with open(args.config, "r") as c:
                cfg = yaml.safe_load(c)
            return cfg
        except FileNotFoundError:
            return None

def main():
    parser = argparse.ArgumentParser(
        description="Use an LLM to solve a CTF challenge",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    model_list = []
    for b in Backend.registry.values():
        model_list += b.get_models()
    model_list = list(set(model_list))

    script_dir = Path(__file__).parent.resolve()

    parser.add_argument("--challenge", help="Name of the challenge")
    parser.add_argument("--dataset", help="Path to the dataset JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="don't print messages to the console")
    parser.add_argument("-d", "--debug", action="store_true", help="print debug messages")
    parser.add_argument("-M", "--model", help="the model to use (default is backend-specific)", choices=model_list)
    parser.add_argument("-C", "--container-image", default="ctfenv", help="the Docker image to use for the CTF environment")
    parser.add_argument("-n", "--container-name", default=f"ctfenv_{os.getuid()}", help="the Docker container name to set for the CTF environment")
    parser.add_argument("-N", "--network", default="ctfnet", help="the Docker network to use for the CTF environment")
    parser.add_argument("-m", "--max-rounds", type=int, default=100, help="maximum number of rounds to run")
    parser.add_argument("-L", "--logdir", default=str(script_dir / "logs"), help="log directory to write the log")
    parser.add_argument("--api-key", default=None, help="API key to use when calling the model")
    parser.add_argument("--api-endpoint", default=None, help="API endpoint URL to use when calling the model")
    parser.add_argument("--backend", default="openai", choices=Backend.registry.keys(), help="model backend to use")
    parser.add_argument("--formatter", default="xml", choices=Formatter.registry.keys(), help="prompt formatter to use")
    parser.add_argument("--prompt-set", default="default", help="set of prompts to use")
    parser.add_argument("--hints", default=[], nargs="+", help="list of hints to provide")
    parser.add_argument("--disable-docker", default=False, action="store_true", help="disable Docker usage (for debugging)")
    parser.add_argument("--disable-markdown", default=False, action="store_true", help="don't render Markdown formatting in messages")
    parser.add_argument("--max-cost", type=float, default=10, help="maximum cost of the conversation to run")

    # Newly added config options
    parser.add_argument("--experiment-name", default="default", help="Experiment name tag")
    parser.add_argument("--skip_exist", default=False, action="store_true", help="Skip existing logs and experiments")
    parser.add_argument("-c", "--config", default=None, help="Config file to run the experiment")
    parser.add_argument("-i", "--index", default=0, help="Round index of the experiment")
    # TODO remove script_dir
    parser.add_argument("-L", "--logdir", default=str(script_dir / "logs" / getpass.getuser()), help="log directory to write the log")

    args = parser.parse_args()
    config: dict = load_config(args=args)
    overwrite_args(args, config)
    status.set(quiet=args.quiet, debug=args.debug, disable_markdown=args.disable_markdown)

    dataset = CTFDataset(args.dataset)
    challenge = CTFChallenge(dataset.get(args.challenge), dataset.basedir)
    logfile = Path(args.logdir).resolve() / f"{challenge.canonical_name}.json"
    
    if not os.path.exists(logfile) or not args.skip_exist:
        if not args.skip_exist and os.path.exists(logfile):
            os.remove(logfile)
        with CTFEnvironment(challenge=challenge, args=args) as env, \
            CTFConversation(env, args, config=config) as convo:
            convo.run()
    else:
        status.print(f"[red bold]Challenge log {logfile} exists; skipping[/red bold]", markup=True)

    # Create logfile
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logdir = Path(args.logdir).expanduser().resolve()
    logdir.mkdir(parents=True, exist_ok=True)
    logfile = logdir / f"{challenge.canonical_name}-{timestamp}.json"

    environment = CTFEnvironment(challenge, args.container_image, args.network)
    prompt_manager = PromptManager(prompt_set=args.prompt_set, config=config)
    backend = Backend.from_name(args.backend)(prompt_manager.system_message(challenge), environment.available_tools, model=args.model, api_key=args.api_key)

    with CTFConversation(environment, challenge, prompt_manager, backend, logfile, max_rounds=args.max_rounds, max_cost=args.max_cost) as convo:
        convo.run()

if __name__ == "__main__":
    main()
