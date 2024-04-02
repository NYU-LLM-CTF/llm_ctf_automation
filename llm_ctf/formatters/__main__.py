from . import Formatter
import argparse
from ..tools import DEFAULT_TOOLSET, CommandExec, CheckFlag, GiveUp, ToolResult

def demo_formatter(formatter_name: str):
    def section_header(title: str):
        return f' {title} '.center(80, '=')
    tools = {
        tool.name: tool for tool in DEFAULT_TOOLSET
    }
    formatter = Formatter.from_name(formatter_name)(tools=DEFAULT_TOOLSET)
    print('*' * 80)
    print(f"* {formatter_name+' formatter':^76} *")
    print('*' * 80)
    print()
    print(section_header('Available Tools'))
    print(formatter.format_tools(DEFAULT_TOOLSET))
    print(section_header('Tool Calls'))
    tool_calls = [
        CommandExec.make_call(command="uname -a"),
        CommandExec.make_call(command="nc example.com 80", timeout=25),
        CheckFlag.make_call(flag="csawctf{example_flag}"),
        GiveUp.make_call(confirm='false'),
    ]
    print(f"Note: tool call IDs are: {[tc.id for tc in tool_calls]}")
    formatted = formatter.format_tool_calls(tool_calls)
    print(formatted)
    print(section_header('Extracted Tool Calls'))
    extracted = formatter.extract_tool_calls(formatted)
    for e in extracted:
        print(f"Tool call: {e.name}")
        print(f"Call ID: {e.id}")
        print(f"Arguments: {e.function.arguments}")
        parsed_tc = formatter.extract_params(tools[e.name], e)
        print(f"Parsed arguments: {parsed_tc.function.parsed_arguments}")
    print(section_header('Tool Results'))
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
        ToolResult(tc.name, tc.id, tr) for tc, tr in zip(extracted, tool_results)
    ]
    print(formatter.format_results(tool_results))
    print(section_header('Start/Stop Sequences'))
    starts, stops = formatter.get_delimiters()
    print(f"Start: {starts}")
    print(f" Stop: {stops}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formatter demo tool")
    parser.add_argument("formatters", metavar='FORMATTER', nargs='*', type=str, help="Formatter to use")
    args = parser.parse_args()
    if not args.formatters:
        print("Supported formatters:")
        for formatter in Formatter.names():
            print(f"  - {formatter}")
    else:
        for formatter in args.formatters:
            demo_formatter(formatter)
