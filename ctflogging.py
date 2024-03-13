from rich.console import Console
from rich.markdown import Markdown

class Status:
    def __init__(self, quiet=False, debug=False):
        self.quiet = quiet
        self.debug = debug
        self._last = None
        self.console = Console(markup=False, highlight=False, color_system="256")
        self.debug_log = []

    def set(self, quiet=None, debug=None):
        if quiet is not None: self.quiet = quiet
        if debug is not None: self.debug = debug

    # Helper functions for printing messages, with colors
    # and nice wrapping
    def assistant_message(self, message):
        if message is None:
            return
        if not self.quiet:
            self.console.print("\n[Assistant]", style="blue bold")
            self.console.print(Markdown(message), width=72)
            self._last = "ASSISTANT"

    def user_message(self, message):
        if message is None:
            return
        if not self.quiet:
            print()
            self.console.print("\n[User]", style="green bold")
            self.console.print(Markdown(message), width=72)
            self._last = "USER"

    def system_message(self, message):
        if not self.quiet:
            self.console.print("System Prompt:", style="red bold")
            self.console.print(Markdown(message), width=72)
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
        self.console.print(*args, **kwargs)

status = Status()
