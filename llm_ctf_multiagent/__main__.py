import argparse

from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge

from .environment import CTFEnvironment
from .backends.openai_backend import OpenAIBackend
from .prompting import PromptManager
from .agent import BaseAgent

parser = argparse.ArgumentParser(description="Multi-agent LLM for CTF solving")

parser.add_argument("--challenge", required=True, help="Name of the challenge")
parser.add_argument("--dataset", help="Dataset JSON path. Only provide if not using the NYUCTF dataset at default path")
parser.add_argument("-s", "--split", default="development", choices=["test", "development"], help="Dataset split to select. Only used when --dataset not provided.")
parser.add_argument("--api-key", required=True, help="OpenAI API key") # TODO remove later

args = parser.parse_args()

if args.dataset is not None:
    dataset = CTFDataset(dataset_json=args.dataset)
else:
    dataset = CTFDataset(split=args.split)
challenge = CTFChallenge(dataset.get(args.challenge), dataset.basedir)
environment = CTFEnvironment(challenge, "ctfenv", "ctfnet")

# TODO configurable
backend = OpenAIBackend("gpt-4o-mini", environment.available_tools, args.api_key)

prompt_manager = PromptManager("config/prompts/base_prompt.yaml", challenge, environment)

agent = BaseAgent(environment, challenge, prompt_manager, backend)
agent.run()
