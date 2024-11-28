import argparse

from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

from .environment import CTFEnvironment
from .backends.openai_backend import OpenAIBackend
from .prompting import PromptManager
from .agent import PlannerExecutorSystem
from .logging import status

parser = argparse.ArgumentParser(description="Multi-agent LLM for CTF solving")

parser.add_argument("--challenge", required=True, help="Name of the challenge")
parser.add_argument("--dataset", help="Dataset JSON path. Only provide if not using the NYUCTF dataset at default path")
parser.add_argument("-s", "--split", default="development", choices=["test", "development"], help="Dataset split to select. Only used when --dataset not provided.")
parser.add_argument("--api-key", required=True, help="OpenAI API key") # TODO remove later

args = parser.parse_args()

status.set(quiet=False, debug=True)

if args.dataset is not None:
    dataset = CTFDataset(dataset_json=args.dataset)
else:
    dataset = CTFDataset(split=args.split)
challenge = CTFChallenge(dataset.get(args.challenge), dataset.basedir)

# TODO configurable
environment = CTFEnvironment(challenge, "ctfenv:multiagent", "ctfnet")
planner_backend = OpenAIBackend("gpt-4o", environment.get_toolset("planner"), args.api_key)
planner_prompter = PromptManager("config/prompts/planner_prompt.yaml", challenge, environment)
executor_backend = OpenAIBackend("gpt-4o", environment.get_toolset("executor"), args.api_key)
executor_prompter = PromptManager("config/prompts/executor_prompt.yaml", challenge, environment)

with PlannerExecutorSystem(environment, challenge, planner_prompter, planner_backend, executor_prompter, executor_backend) as multiagent:
    multiagent.run()
