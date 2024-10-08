from rich.console import Console
from rich.markdown import Markdown

class Status:
    WIDTH = 72
    THEME = "default"
    def __init__(self, quiet=False, debug=False):
        self.quiet = quiet
        self.debug = debug
        self.disable_markdown = False
        self._last = None
        self.console = Console(markup=False, highlight=False, color_system="256")
        self.debug_log = []

    def set(self, quiet=None, debug=None, disable_markdown=None):
        if quiet is not None: self.quiet = quiet
        if debug is not None: self.debug = debug
        if disable_markdown is not None: self.disable_markdown = disable_markdown

    # Helper functions for printing messages, with colors
    # and nice wrapping
    def assistant_message(self, message):
        if message is None:
            return
        if not self.quiet:
            self.console.print("\n[Assistant]", style="blue bold")
            if not self.disable_markdown:
                m = Markdown(message, code_theme=self.THEME)
            else:
                m = message
            self.console.print(m, width=self.WIDTH)
            self._last = "ASSISTANT"

    def user_message(self, message):
        if message is None:
            return
        if not self.quiet:
            print()
            self.console.print("\n[User]", style="green bold")
            if not self.disable_markdown:
                m = Markdown(message, code_theme=self.THEME)
            else:
                m = message
            self.console.print(m, width=self.WIDTH)
            self._last = "USER"
            
    def hint_message(self, message):
        if not self.quiet:
            self.console.print("[Hint Prompt]\n", style="yellow bold")
            if not self.disable_markdown:
                m = Markdown(message, code_theme=self.THEME)
            else:
                m = message
            self.console.print(m, width=self.WIDTH)
            self._last = "HINT"

    def system_message(self, message):
        if not self.quiet:
            self.console.print("[System Prompt]\n", style="red bold")
            if not self.disable_markdown:
                m = Markdown(message, code_theme=self.THEME)
            else:
                m = message
            self.console.print(m, width=self.WIDTH)
            self._last = "SYSTEM"

    def debug_message(self, message, truncate=False):
        if message is None:
            return
        self.debug_log.append(message)
        if self.debug:
            if self._last != "DEBUG": self.console.print()
            if truncate and len(message) > 100:
                self.console.print(f"DEBUG: {message[:100].strip()}...", style="dim")
            else:
                self.console.print(f"DEBUG: {message}", style="dim")
            self._last = "DEBUG"

    def print(self, *args, **kwargs):
        if not self.quiet:
            self.console.print(*args, **kwargs)

status = Status()
