#!/usr/bin/env python3

from collections import defaultdict
from typing import List, TYPE_CHECKING
from jinja2 import Environment, PackageLoader, StrictUndefined
from jinja2.exceptions import TemplateNotFound

from ..challenge import CTFChallenge
from ..tools import Tool, ToolCall, ToolResult
if TYPE_CHECKING:
    from ..formatters import Formatter
import os

DEFAULT_PROMPT_SET = 'default'

def blockquote(text):
    return '\n'.join([f'> {line}' for line in text.split('\n')])

class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), template))

class FallbackLoader(PackageLoader):
    """A Jinja2 loader that falls back to a default collection."""
    def __init__(
            self,
            package_name: str,
            package_path: str = "templates",
            encoding: str = "utf-8",
            prompt_set: str = DEFAULT_PROMPT_SET) -> None:
        super().__init__(package_name, package_path, encoding)
        self.prompt_set = prompt_set

    def get_source(self, environment, template):
        try:
            return super().get_source(environment, os.path.normpath(f'{self.prompt_set}/{template}'))
        except TemplateNotFound:
            return super().get_source(environment, os.path.normpath(f'{DEFAULT_PROMPT_SET}/{template}'))

class PromptManager:
    def __init__(self, prompt_set=DEFAULT_PROMPT_SET):
        self.prompt_set = prompt_set
        self.env = RelEnvironment(
            loader=FallbackLoader('llm_ctf.prompts', prompt_set=prompt_set),
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.do'],
        )
        self.env.filters['blockquote'] = blockquote
        self.prompts = {}

    def render(self, name, **kwargs):
        if name not in self.prompts:
            self.prompts[name] = self.env.get_template(f'{name}.md.jinja2')
        return self.prompts[name].render(**kwargs)

    def tool_use(
            self,
            formatter : 'Formatter',
            tools : List[Tool],
            example_call : ToolCall = None,
            **kwargs
        ):
        tool_use_example = formatter.format_tool_calls(
            [example_call] if example_call else [],
            placeholder=True,
            **kwargs,
        )
        return self.render(
            'tool_use',
            tool_list=formatter.format_tools(tools),
            tool_use_example=tool_use_example,
            formatter=formatter,
        )

    def tool_calls(
            self,
            formatter: 'Formatter',
            tool_calls: List[ToolCall],
            **kwargs):
        return self.render(
            'tool_calls',
            formatter=formatter,
            tool_calls=formatter.format_tool_calls(tool_calls),
            **kwargs,
        )

    def tool_results(
            self,
            formatter: 'Formatter',
            tool_results: List[ToolResult],
            **kwargs):
        return self.render(
            'tool_results',
            formatter=formatter,
            tool_results=formatter.format_results(tool_results),
            **kwargs
        )

    def initial_message(self, chal: CTFChallenge, **kwargs):
        return self.render('initial_message', chal=chal, **kwargs)

    def get_chal_hint(self, chal: CTFChallenge, hint: str):
        """Get hint from the challenge dir. Return None if not present."""
        hintpath = chal.chaldir / f"hints/{hint}.md"
        if not hintpath.exists():
            return None
        return hintpath.read_text()

    def hints_message(self, chal: CTFChallenge, hints=[], **kwargs):
        """
        Look for hints in the the challenge folder and templates folder.
        """
        msg = []
        for hint in hints:
            if ht := self.get_chal_hint(chal, hint):
                # Look in challenge dir
                msg.append(ht)
            else:
                try:
                    # Look for common template
                    msg.append(self.render(f"hints/{chal.category}/{hint}", chal=chal, **kwargs))
                except TemplateNotFound:
                    pass
        return "\n\n".join(msg)

    def keep_going(self, **kwargs):
        return self.render('keep_going', **kwargs)

    def system_message(self, chal, **kwargs):
        return self.render('system', chal=chal, **kwargs)
