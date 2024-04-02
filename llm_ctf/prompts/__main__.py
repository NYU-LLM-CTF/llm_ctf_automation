import argparse
from pathlib import Path
import random
import sys

from .prompts import PromptManager
from ..backends.vllm_backend import VLLMBackend, MODELS
from ..formatters import Formatter
from ..challenge import CTFChallenge
from ..ctflogging import status
from ..tools import DEFAULT_TOOLSET, CommandExec, CheckFlag, GiveUp, ToolCall, ToolResult
from rich.console import Console
from rich.markdown import Markdown

def section_header(title: str):
    return f' {title} '.center(80, '=')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prompt demo tool")
    parser.add_argument("challenge_json", type=Path, help="path to the JSON file describing the challenge")
    parser.add_argument("-p", "--prompt-set", type=str, help="Set of prompts to use", default='default')
    parser.add_argument("-f", "--formatter", choices=Formatter.registry.keys(), type=str, help="Formatter to use", default="xml")
    parser.add_argument('-m', '--markdown', action='store_true', help='Show the prompts with Markdown rendered')
    parser.add_argument('-t', '--theme', type=str, help='Theme to use for Markdown code blocks', default='default')
    parser.add_argument('-n', '--no-debug', action='store_true', help='Suppress debug output')
    args = parser.parse_args()

    if args.no_debug:
        status.set(quiet=False, debug=False)
    else:
        status.set(quiet=False, debug=True)
    status.THEME = args.theme
    if args.markdown:
        console = Console(markup=False, highlight=False, color_system="256")
        print_fn = lambda s: console.print(Markdown(s), width=80)
    else:
        print_fn = print
    formatter = Formatter.from_name(args.formatter)(tools=DEFAULT_TOOLSET, prompt_set=args.prompt_set)
    pc = PromptManager(args.prompt_set)

    # Fake CLI args
    fake_args = argparse.Namespace(
        container_image="ctfenv",
        # Add a randomly generated suffix to the container name
        container_name=f"ctfenv-{random.randint(1000, 9999):04d}",
        network="ctfnet",
        disable_docker=False,
        prompt_set=args.prompt_set,
        formatter=args.formatter,
        model=MODELS[0],
        api_endpoint="http://example.com",
        debug=not args.no_debug,
    )
    chal = CTFChallenge(args.challenge_json, fake_args)

    print(section_header("System Message"))
    system_message = pc.render("system")
    print_fn(system_message)

    print(section_header("System Message (Tool Use)"))
    example_call = ToolCall.create_parsed("$TOOL_NAME", "$CALL_ID", {"$PARAMETER_NAME": "$PARAMETER_VALUE"})
    print_fn(pc.tool_use(
        formatter,
        DEFAULT_TOOLSET,
        example_call,
    ))

    print(section_header("Initial Message"))
    print_fn(pc.initial_message(chal))

    print(section_header("Keep Going Message"))
    print_fn(pc.keep_going(tools=DEFAULT_TOOLSET))

    print(section_header("Tool Calls"))
    tool_calls = [
        CommandExec.make_call(command="uname -a"),
        CommandExec.make_call(command="nc example.com 80", timeout=25),
        CheckFlag.make_call(flag="csawctf{example_flag}"),
        GiveUp.make_call(confirm='false'),
    ]
    print_fn(pc.tool_calls(formatter, tool_calls=tool_calls))

    print(section_header("Tool Results"))
    tool_results = [
        dict(stdout="Linux example 5.4.0-91-generic #102-Ubuntu SMP Fri Nov 5 16:31:28 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux\n",
                stderr="",
                returncode=0,
                timed_out=False),
        dict(stdout="Welcome to the server!\nInput: ", stderr="", returncode=0, timed_out=True),
        dict(correct=True),
        dict(error="You must confirm that you want to give up"),
    ]
    tool_results = [
        ToolResult(tc.name, tc.id, tr) for tc, tr in zip(tool_calls, tool_results)
    ]
    print_fn(pc.tool_results(formatter,tool_results))

    print(section_header("Tool Use Demo Messages"))
    exc_info = None
    try: # Do all this in a try block so we can tear down the tools afterwards
        # Instantiate the tools
        tools = [tool(chal) for tool in DEFAULT_TOOLSET]
        tool_dict = {tool.name: tool for tool in tools}
        for t in tools:
            t.setup()
        # Get the VLLM backend
        backend = VLLMBackend(system_message=pc.render("system"), tools=tools, args=fake_args)
        backend.make_demo_from_templates()
        for message in backend.model_messages:
            if message['role'] == 'user':
                status.user_message(message['content'])
            elif message['role'] == 'assistant':
                content = message['content']
                if formatter.get_delimiters()[0][0] in message['content']:
                    content = "🤔 ...thinking... 🤔\n\n" + content
                status.assistant_message(content)
            else:
                status.system_message(message['content'])
    except Exception as e:
        exc_info = sys.exc_info()
        raise
    finally:
        if exc_info is None:
            exc_info = (None, None, None)
        for t in tools:
            t.teardown(*exc_info)
