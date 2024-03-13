#!/usr/bin/env python3

import json
import sys
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, TextLexer, CLexer, NasmLexer, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound
from ctflogging import status

def print_create_file(args, result):
    filename = result['path']
    content = args['contents']
    try:
        lexer = guess_lexer_for_filename(filename, content)
    except ClassNotFound:
        try:
            lexer = guess_lexer(content)
        except ClassNotFound:
            lexer = TextLexer()
    formatter = TerminalFormatter()
    print(f"Create file {filename}:")
    print(highlight(content, lexer, formatter))

def print_run_command(args, result):
    ret = result['returncode']
    timed_out = " (timed out)" if result['timed_out'] else ""
    print(f"Command exec with ret={ret}{timed_out}:")
    command = args['command']
    stdout = result['stdout']
    stderr = result['stderr']
    print(f"$ {command}")
    if stdout:
        print(f"==> stdout:\n{stdout}")
    if stderr:
        print(f"==> stderr:\n{stderr}")

def print_decompile(args, result):
    binary = args['binary']
    function = args.get('function', 'main')
    code = result['decompilation']
    print(f"Decompiled {binary} function {function}:")
    lexer = CLexer()
    formatter = TerminalFormatter()
    print(highlight(code, lexer, formatter))

def print_disassemble(args, result):
    binary = args['binary']
    function = args.get('function', 'main')
    code = result['disassembly']
    print(f"Disassembled {binary} function {function}:")
    lexer = NasmLexer()
    formatter = TerminalFormatter()
    print(highlight(code, lexer, formatter))

def print_command(name, args, result):
    if args is None:
        argstr = '[missing]'
    else:
        argstr = ', '.join(f'{k}={repr(v)}' for k, v in args.items())
    if 'error' in result:
        print(f"{name}({argstr}) failed: {result['error']}")
        return
    if name == "run_command":
        print_run_command(args, result)
    elif name == "createfile":
        print_create_file(args, result)
    elif name == "decompile_function":
        print_decompile(args, result)
    elif name == "disassemble_function":
        print_disassemble(args, result)
    else:
        print(f"{name}({argstr}):")
        for k,v in result.items():
            print(f"==> {k}:\n{v}")

pretty_finish_reasons = {
    "exception": "an exception was raised",
    "max_rounds": "the maximum number of rounds was reached",
    "user_cancel": "the user cancelled the conversation",
    "give_up": "the assistant gave up",
    "solved": "the problem was solved",
    "unknown": "of an unknown reason"
}

calls = {}
js = json.load(open(sys.argv[1]))
model = js['args']['model']
print(f"Log of conversation with {model} on {js['start_time']} to {js['end_time']} ({js['runtime_seconds']} seconds)")
solve_str = "solved successfully" if js['solved'] else "not solved"
print(f"Conversation lasted {js['rounds']} rounds and was {solve_str}")
if 'finish_reason' in js:
    print(f"Conversation ended because {pretty_finish_reasons[js['finish_reason']]}.")
if 'exception_info' in js and js['exception_info']:
    print()
    print("Conversation ended with exception:")
    print("Traceback (most recent call last):")
    print(f"{js['exception_info']['traceback']}")
    status.console.print(f"[red bold]{js['exception_info']['exception_type']}[/red bold]: {js['exception_info']['exception_message']}",
                            markup=True)
    print()
print("*"*80)
for message in js['messages']:
    if message['content']:
        if message['role'] == 'system':
            status.system_message(message['content'])
        elif message['role'] == 'user':
            status.user_message(message['content'])
        elif message['role'] == 'assistant':
            status.assistant_message(message['content'])

    if message['role'] == 'assistant' and not message['content']:
        status.assistant_message("🤔 ...thinking... 🤔")

    if 'tool_calls' in message and message['tool_calls']:
        for tool_call in message['tool_calls']:
            call_id = tool_call['id']
            function = tool_call['function']
            name = function['name']
            try:
                args = json.loads(function['arguments'])
            except json.JSONDecodeError:
                args = {'error': f'error decoding {function["arguments"]}'}
            calls[call_id] = (name, args)
        print()
        print(f"Use tools: {', '.join(call['function']['name'] for call in message['tool_calls'])}")
        print()
    elif message['role'] == 'tool':
        call_id = message['tool_call_id']
        name = message['name']
        if call_id in calls:
            args = calls[call_id][1]
        else:
            args = None
        result = json.loads(message['content'])
        print_command(name, args, result)
    print("="*80)
