from datetime import datetime
import socket
import subprocess
import time
import json
import os
import argparse
import shutil
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

    parser.add_argument("--challenge", required=True, help="Name of the challenge")
    parser.add_argument("--dataset", required=True, help="Path to the dataset JSON")
    parser.add_argument("-c", "--config", help="Config file to run the experiment")

    parser.add_argument("-q", "--quiet", action="store_true", help="don't print messages to the console")
    parser.add_argument("-d", "--debug", action="store_true", help="print debug messages")
    parser.add_argument("-M", "--model", help="the model to use (default is backend-specific)", choices=model_list)
    parser.add_argument("-C", "--container-image", default="ctfenv", help="the Docker image to use for the CTF environment")
    parser.add_argument("-N", "--network", default="ctfnet", help="the Docker network to use for the CTF environment")
    parser.add_argument("--api-key", default=None, help="API key to use when calling the model")
    parser.add_argument("--api-endpoint", default=None, help="API endpoint URL to use when calling the model")
    parser.add_argument("--backend", default="openai", choices=Backend.registry.keys(), help="model backend to use")
    parser.add_argument("--formatter", default="xml", choices=Formatter.registry.keys(), help="prompt formatter to use")
    parser.add_argument("--prompt-set", default="default", help="set of prompts to use")
    # TODO add back hints functionality
    # parser.add_argument("--hints", default=[], nargs="+", help="list of hints to provide")
    parser.add_argument("--disable-markdown", default=False, action="store_true", help="don't render Markdown formatting in messages")
    parser.add_argument("-m", "--max-rounds", type=int, default=10, help="maximum number of rounds to run")
    parser.add_argument("--max-cost", type=float, default=10, help="maximum cost of the conversation to run")

    # Log directory options
    parser.add_argument("--skip-exist", action="store_true", help="Skip existing logs and experiments")
    parser.add_argument("-L", "--logdir", default=str(script_dir / "logs" / os.getlogin()), help="log directory to write the log")
    parser.add_argument("-n", "--name", help="Experiment name (creates subdir in logdir)")
    parser.add_argument("-i", "--index", help="Round index of the experiment (creates subdir in logdir)")
    parser.add_argument("--hints", type=list, default=[], help="A list of hints file")

    args = parser.parse_args()
    config = None
    if args.config:
        try:
            with open(args.config, "r") as c:
                config = yaml.safe_load(c)
        except FileNotFoundError:
            pass

    if config:
        config_parameter = config.get("parameter", {})
        config_experiment = config.get("experiment", {})
        config_demostration = config.get("demostration", {})

        args.max_rounds = config_parameter.get("max_rounds", args.max_rounds)
        args.backend = config_parameter.get("backend", args.backend)
        args.model = config_parameter.get("model", args.model)
        args.max_cost = config_parameter.get("max_cost", args.max_cost)
        args.name = config_experiment.get("name", args.name)
        args.debug = config_experiment.get("debug", args.debug)
        args.skip_exist = config_experiment.get("skip_exist", args.skip_exist)
        args.hints = config_demostration.get("hints", [])

    status.set(quiet=args.quiet, debug=args.debug, disable_markdown=args.disable_markdown)

    dataset = CTFDataset(args.dataset)
    challenge = CTFChallenge(dataset.get(args.challenge), dataset.basedir)

    logdir = Path(args.logdir).expanduser().resolve()
    logsubdir = []
    if args.name:
        logsubdir.append(args.name)
    if args.index:
        logsubdir.append(f"round{args.index}")
    if len(logsubdir) > 0:
        logdir = logdir / ("_".join(logsubdir))
    logdir.mkdir(parents=True, exist_ok=True)
    logfile = logdir / f"{challenge.canonical_name}.json"
    
    if logfile.exists() and args.skip_exist:
        status.print(f"[red bold]Challenge log {logfile} exists; skipping[/red bold]", markup=True)
        exit()
        
    environment = CTFEnvironment(challenge, args.container_image, args.network)
    prompt_manager = PromptManager(prompt_set=args.prompt_set, config=config)
    backend = Backend.from_name(args.backend)(prompt_manager.system_message(challenge), prompt_manager.hints_message(), environment.available_tools, args)

    with CTFConversation(environment, challenge, prompt_manager, backend, logfile, max_rounds=args.max_rounds, max_cost=args.max_cost, args=args) as convo:
        convo.run()

if __name__ == "__main__":
    main()
