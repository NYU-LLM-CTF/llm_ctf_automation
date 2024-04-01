from . import Formatter
import argparse
from ..tools import DEFAULT_TOOLSET, CommandExec, CheckFlag, GiveUp

def demo_formatter(formatter_name: str):
    tools = {
        tool.name: tool for tool in DEFAULT_TOOLSET
    }
    formatter = Formatter.from_name(formatter_name)(tools=DEFAULT_TOOLSET)
    print(f"Example output for {formatter_name}:")
    print(f"===================== {'Available Tools':^20} =====================")
    print(formatter.format_tools(DEFAULT_TOOLSET))
    print(f"===================== {'Tool Calls':^20} =====================")
    tool_calls = [
        CommandExec.make_call(command="uname -a"),
        CommandExec.make_call(command="nc example.com 80", timeout=25),
        CheckFlag.make_call(flag="csawctf{example_flag}"),
        GiveUp.make_call(confirm='false'),
    ]
    print(f"Note: tool call IDs are: {[tc.id for tc in tool_calls]}")
    formatted = formatter.format_tool_calls(tool_calls)
    print(formatted)
    print(f"===================== {'Extracted Tool Calls':^20} =====================")
    extracted = formatter.extract_tool_calls(formatted)
    for e in extracted:
        print(f"Tool call: {e.name}")
        print(f"Call ID: {e.id}")
        print(f"Arguments: {e.function.arguments}")
        parsed_tc = formatter.extract_params(tools[e.name], e)
        print(f"Parsed arguments: {parsed_tc.function.parsed_arguments}")
    print(f"===================== {'Tool Results':^20} =====================")
    # print(formatter.format_results(DEFAULT_TOOLSET[0].results))
    print(f"===================== {'Start/Stop Sequences':^20} =====================")
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
