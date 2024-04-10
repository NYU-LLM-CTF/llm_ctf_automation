from argparse import Namespace
from pathlib import Path
from typing import Any, Callable, List, Literal, Tuple, Optional, NamedTuple, Union
import re
import os

from anthropic import Anthropic
from anthropic.types.content_block import ContentBlock as AnthropicMessage

from llm_ctf.formatters.vbpy import VBPYFormatter
from ..formatters.formatter import Formatter
from ..tools import Tool, ToolCall, ToolResult
from ..ctflogging import status
from .backend import (AssistantMessage, Backend, ErrorToolCalls, FakeToolCalls,
                      SystemMessage, UnparsedToolCalls, UserMessage)
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from functools import partial
from rich.syntax import Syntax
from rich.pretty import Pretty
PythonSyntax = partial(Syntax, lexer="python", theme=status.THEME, line_numbers=False)

# Mixtral has an unfortunate habit of escaping underscores in its
# XML tag names. Fix that here:
XML_TAG_REGEX = re.compile(r'<[^>]*?>')
def fix_xml_tag_names(s : str) -> str:
    # Process each XML tag separately to handle multiple escaped underscores
    def unescape_underscores(match : re.Match):
        # Replace all escaped underscores within the tag
        return match.group(0).replace(r'\_', '_')
    # Find all XML tags and apply the unescape function
    return XML_TAG_REGEX.sub(unescape_underscores, s)

def fix_xml_seqs(seqs : List[str]) -> List[str]:
    return list(set(seqs +[fix_xml_tag_names(seq) for seq in seqs]))

class ModelQuirks(NamedTuple):
    """Model-specific quirks for the VLLM backend."""
    # Whether the model supports system messages
    supports_system_messages: bool
    # Whether the model needs tool use demonstrations (most do)
    needs_tool_use_demonstrations: bool = True
    # Function to run to clean up the model's content output
    clean_content: Optional[Callable[[str], str]] = None
    # Function to run to clean up the model's tool output
    clean_tool_use: Optional[Callable[[str], str]] = None
    # Function to run to augment the stop sequences from the formatter
    augment_stop_sequences: Optional[Callable[[List[str]], List[str]]] = None
    # Function to run to augment the start sequences from the formatter
    augment_start_sequences: Optional[Callable[[List[str]], List[str]]] = None

NO_QUIRKS = ModelQuirks(supports_system_messages=True)

class VLLMBackend(Backend):
    NAME = 'vllm'
    MODELS = [
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "deepseek-ai/deepseek-coder-33b-instruct",
    ]
    QUIRKS = {
        "mistralai/Mixtral-8x7B-Instruct-v0.1": ModelQuirks(
            supports_system_messages=False,
            needs_tool_use_demonstrations=True,
            clean_content=fix_xml_tag_names,
            clean_tool_use=fix_xml_tag_names,
            augment_stop_sequences=fix_xml_seqs,
            augment_start_sequences=fix_xml_seqs,
        ),
    }

    def __init__(self, system_message : str, tools: dict[str,Tool], args : Namespace):
        self.args = args
        self.formatter : Formatter = Formatter.from_name(args.formatter)(tools, args.prompt_set)
        self.prompt_manager = self.formatter.prompt_manager
        self.tools = tools

        if args.model:
            if args.model not in self.MODELS:
                raise ValueError(f"Invalid model {args.model} for backend. Must be one of {self.MODELS}")
            self.model = args.model
        else:
            self.model = self.MODELS[0]
            # Update the args object so that the model name will be included in the logs
            args.model = self.model

        self.client_setup(args)
        self.quirks = self.QUIRKS.get(self.model, NO_QUIRKS)
        self.system_message_content = system_message

        # Get the vbpy formatter so we can use it to represent a tool call as a
        # nice Python string
        self.python_formatter = VBPYFormatter(tools, args.prompt_set)

        self.outgoing_messages = []
        self.last_tool_calls = None

    def client_setup(self, args):
        if args.api_endpoint:
            base_url = args.api_endpoint
        else:
            base_url = "http://isabella:8000/v1"
        self.client = OpenAI(
            api_key = "EMPTY",
            base_url=base_url
        )

    @classmethod
    def get_models(cls):
        return cls.MODELS

    def setup(self):
        self.add_initial_messages()

    def demo_tool_call(self, tool_name: str, args: dict[str, Any], out:List) -> Literal[""]:
        tool = self.tools[tool_name]
        tool_call = tool.make_call(**args)
        out.append(tool_call)
        return ""

    def tool_demo(self, template):
        tool_calls: List[ToolCall] = []
        def render_tool_calls():
            return self.prompt_manager.tool_calls(self.formatter, tool_calls)
        tool_calls_content = self.prompt_manager.render(
            template,
            make_tool_call=self.demo_tool_call,
            dest=tool_calls,
            render_tool_calls=render_tool_calls,
        )
        self.messages.append(FakeToolCalls(tool_calls))
        self.append(self.assistant_message(tool_calls_content))
        tool_results = self.run_tools_internal(tool_calls)
        self.append(self.tool_results_message(tool_results))
        # NB: the tool results are not added to self.messages because they are
        # added inside of _run_tools_internal.

    def make_demonstration_messages(self):
        role_states = {
            'user': {'assistant', 'tool'},
            'tool': {'assistant', 'tool'},
            'assistant': {'user'},
        }
        demo_templates = self.prompt_manager.env.list_templates(
            filter_func=lambda s: f'{self.args.prompt_set}/demo_messages' in s
        )
        expected_next_roles = {"user"}
        for msg_num, template in enumerate(sorted(demo_templates)):
            template_name = Path(template).name
            status.debug_message(f"Processing demo message template {template_name}")
            match re.match(r'(\d\d)_(user|assistant|tool)', template_name):
                case None:
                    status.debug_message(f"Warning: demo message template {template} doesn't "
                                         f"match expected format; skipping")
                    continue
                case m:
                    num, role = m.groups()
                    template_stem = f"demo_messages/{m.group(0)}"

            # Do some validation
            if role not in role_states:
                status.debug_message(f"Warning: demo message template {template} has "
                                        f"unexpected role {role}; skipping")
                continue
            if int(num) != msg_num:
                status.debug_message(f"Warning: demo message template {template} has "
                                        f"unexpected number {num}")
            if role not in expected_next_roles:
                status.debug_message(f"Warning: demo message template {template} has "
                                        f"unexpected role {role}; expected one of {expected_next_roles}")
            expected_next_roles = role_states[role]

            # Process the demo message
            match role:
                case "user":
                    content = self.prompt_manager.render(template_stem)
                    self.messages.append(UserMessage(content))
                    self.append(self.user_message(content))
                case "assistant":
                    content = self.prompt_manager.render(template_stem)
                    self.messages.append(AssistantMessage(content))
                    self.append(self.assistant_message(content))
                case "tool":
                    self.tool_demo(template_stem)

    def add_initial_messages(self):
        tool_use_prompt = self.formatter.tool_use_prompt()
        status.debug_message(f"Tool use prompt:\n{tool_use_prompt}")
        self.messages.append(SystemMessage(self.system_message_content, tool_use_prompt))
        self.system_message_content += '\n\n' + tool_use_prompt

        if self.quirks.supports_system_messages:
            system_messages = [
                self.system_message(self.system_message_content),
            ]
        else:
            system_messages = [
                self.user_message(self.system_message_content),
                self.assistant_message("Understood."),
            ]

        for sm in system_messages:
            self.append(sm)

        if self.quirks.needs_tool_use_demonstrations:
            self.make_demonstration_messages()

    def user_message(self, content : str):
        return {"role": "user", "content": content}

    def assistant_message(self, content : str):
        return {"role": "assistant", "content": content}

    def system_message(self, content : str):
        return {"role": "system", "content": content}

    def tool_results_message(self, tool_results : List[ToolResult]):
        return self.user_message(self.formatter.tool_result_prompt(tool_results))

    def tool_calls_message(self, tool_calls : List[ToolCall]):
        return self.assistant_message(self.formatter.tool_call_prompt(tool_calls))

    def call_model_internal(self, start_seqs, stop_seqs):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.outgoing_messages,
            temperature=0.6,
            max_tokens=1024,
            stop=stop_seqs,
            # frequency_penalty=-0.2,
            # Not supported in OpenAI module but VLLM supports it
            extra_body={'repetition_penalty': 1.0},
        )
        # Check if the model wants to run more tools and add the stop sequence
        if response.choices[0].finish_reason == "stop" and any(s in response.choices[0].message.content for s in start_seqs):
            # Add the stop sequence to the content
            response.choices[0].message.content += "\n" + stop_seqs[0] + "\n"
            has_tool_calls = True
        else:
            has_tool_calls = False
        message = response.choices[0].message
        content = message.content
        return response, content, message, has_tool_calls

    # TODO: make generation parameters configurable
    def call_model(self):
        # Get the delimiters from the formatter
        start_seqs, stop_seqs = self.formatter.get_delimiters()
        if self.quirks.augment_stop_sequences:
            stop_seqs = self.quirks.augment_stop_sequences(stop_seqs)
        if self.quirks.augment_start_sequences:
            start_seqs = self.quirks.augment_start_sequences(start_seqs)

        # Make the actual call to the LLM
        (original_response, original_content,
         message, has_tool_calls) = self.call_model_internal(start_seqs, stop_seqs)

        # Some models consistently mess up their output in a predictable and fixable way;
        # apply a fix if one is available.
        if self.quirks.clean_content:
            fixed_content = self.quirks.clean_content(original_content)
        else:
            fixed_content = original_content

        # Extract out the content (as opposed to the tool calls)
        extracted_content = self.formatter.extract_content(fixed_content)

        # Add the cleaned message to the log since the next part may fail
        self.append(message)

        if has_tool_calls:
            # Extract tool calls (but don't parse yet)
            try:
                tool_calls = self.formatter.extract_tool_calls(fixed_content)
                self.messages.append(UnparsedToolCalls(original_response, tool_calls, extracted_content))
                self.last_tool_calls = tool_calls
            except Exception as e:
                estr = f'{type(e).__name__}: {e}'
                status.debug_message(f"Error extracting tool calls: {estr}")
                tool_calls = []
                self.last_tool_calls = None
                self.messages.append(ErrorToolCalls(original_response, estr, extracted_content))
                self.append(
                    self.tool_results_message([
                        ToolResult(
                            name="[error]",
                            id='[none]',
                            results = {"error": f"Error extracting tool calls: {estr}"},
                        )
                    ])
                )
        else:
            self.last_tool_calls = None
            self.messages.append(AssistantMessage(extracted_content, original_response))
        return message, extracted_content, has_tool_calls

    def tool_lookup(self, tool_call : ToolCall) -> Tuple[bool,ToolCall|ToolResult]:
        """Look up a tool by name."""
        # Tool lookup
        tool = self.tools.get(tool_call.name)
        if not tool:
            if tool_call.name == "[not provided]":
                msg = "No tool name provided"
            else:
                msg = f"Unknown tool {tool_call.name}"
            status.debug_message(msg)
            return False, tool_call.error(msg)
        return True, tool

    def parse_tool_call_params(self, tool: Tool, tool_call: ToolCall) -> Tuple[bool, ToolCall | ToolResult]:
        """Extract and parse the parameters for a tool call.

        Returns:
        - (True, tool_call) if successful; the tool_call's parsed_arguments will be set in-place
        - (False, tool_result) if unsuccessful; the tool_result will contain an error message
        """
        # Don't need to parse if the arguments are already parsed;
        # this can happen if the tool call was created with parsed arguments
        if tool_call.parsed_arguments:
            return True, tool_call
        try:
            parsed_tc = self.formatter.extract_params(tool, tool_call)
            # Upgrade in-place so we get the parsed version in the log
            tool_call.parsed_arguments = parsed_tc.parsed_arguments
            return True, tool_call
        except ValueError as e:
            msg = f"{type(e).__name__} extracting parameters for {tool_call.name}: {e}"
            status.debug_message(msg)
            return False, tool_call.error(msg)

    def run_tools_internal(self, tool_calls : List[ToolCall]) -> List[ToolResult]:
        tool_results = []
        for tool_call in tool_calls:

            # Find the tool
            match self.tool_lookup(tool_call):
                case (False, tool_result):
                    tool_results.append(tool_result)
                    self.messages.append(tool_result)
                    continue
                case (True, tool):
                    pass

            # Parse its parameters
            match self.parse_tool_call_params(tool, tool_call):
                case (False, tool_result):
                    tool_results.append(tool_result)
                    self.messages.append(tool_result)
                    continue
                case (True, parsed_tc):
                    pass

            # Tool execution
            if self.args.debug:
                pretty_args = self.python_formatter.format_tool_call(parsed_tc)
                # Remove the '[#function][/#function]' tags
                pretty_args = re.sub(r'\[/?#[^\]]+\]', '', pretty_args)
                status.debug_message(f"Calling {tool.name}:")
                status.print(PythonSyntax(pretty_args), width=status.WIDTH)
            result = tool.run(parsed_tc)
            if self.args.debug:
                status.print(
                    "Result:",
                    Pretty(result.result,max_string=status.WIDTH-30),
                    width=status.WIDTH,
                )
            self.messages.append(result)
            tool_results.append(result)
        return tool_results

    def run_tools(self):
        tool_results = self.run_tools_internal(self.last_tool_calls)
        self.append(self.tool_results_message(tool_results))
        _, content, has_tool_calls = self.call_model()
        return content, has_tool_calls

    def send(self, message : str) -> Tuple[Optional[str],bool]:
        self.append(self.user_message(message))
        self.messages.append(UserMessage(message))
        _, content, has_tool_calls = self.call_model()
        return content, has_tool_calls

    def append(self, message : Union[dict,ChatCompletionMessage,List[ToolResult]]):
        if isinstance(message, dict):
            conv_message = message
        elif isinstance(message, ChatCompletionMessage):
            conv_message = message
        elif isinstance(message, list) and isinstance(message[0], ToolResult):
            conv_message = self.tool_results_message(message)
        else:
            raise ValueError(f"Unknown message type: {type(message)}")
        # Save the message to the log we pass back to the model
        self.outgoing_messages.append(conv_message)

    def get_system_message(self):
        return self.system_message_content

class AnthropicBackend(VLLMBackend):
    NAME = 'anthropic'
    MODELS = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
    ]
    QUIRKS = {
        "claude-3-haiku-20240307": NO_QUIRKS,
        "claude-3-sonnet-20240229": NO_QUIRKS,
        "claude-3-opus-20240229": NO_QUIRKS,
    }
    API_KEY_PATH = "~/.config/anthropic/api_key"

    def client_setup(self, args):
        if args.api_key is None:
            if "ANTHROPIC_API_KEY" in os.environ:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            elif os.path.exists(os.path.expanduser(self.API_KEY_PATH)):
                api_key = open(os.path.expanduser(self.API_KEY_PATH), "r").read().strip()
            else:
                raise ValueError(f"No Anthropic API key provided and none found in ANTHROPIC_API_KEY or {self.API_KEY_PATH}")
        os.environ["ANTHROPIC_API_KEY"] = api_key
        self.client = Anthropic(api_key=api_key)

    def append(self, message : dict|AnthropicMessage|List[ToolResult]):
        if isinstance(message, dict):
            conv_message = message
        elif isinstance(message, list):
            conv_message = self.tool_results_message(message)
        elif isinstance(message, AnthropicMessage):
            conv_message = {
                "role": "assistant",
                "content": message.text,
            }
        else:
            raise ValueError(f"Unknown message type: {type(message)}")
        self.outgoing_messages.append(conv_message)
        self.messages.append(message)

    def call_model_internal(self, start_seqs, stop_seqs):
        start_seqs, stop_seqs = self.formatter.get_delimiters()
        response = self.client.messages.create(
            model=self.model,
            messages=self.outgoing_messages[1:], # Skip system message
            temperature=1,
            max_tokens=1024,
            stop_sequences=stop_seqs,
            system=self.get_system_message(),
        )
        if response.stop_reason == "stop_sequence":
            response.content[0].text += response.stop_sequence

        if any(s in response.content[0].text for s in start_seqs):
            has_tool_calls = True
        else:
            has_tool_calls = False
        status.debug_message(f"Response:\n{response.content[0].text}", truncate=False)
        message = response.content[0]
        return response, message.text, message, has_tool_calls
