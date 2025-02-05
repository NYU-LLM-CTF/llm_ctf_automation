from rich.console import Console
from rich.markdown import Markdown
from rich.status import Status

class Logger:
    WIDTH = 120
    THEME = "default"
    def __init__(self, quiet=False, debug=False):
        self.quiet = quiet
        self.debug = debug
        self._last = None
        self.console = Console(markup=False, highlight=False, color_system="256")
        self.progress = None
        self.debug_log = []

    def set(self, quiet=None, debug=None):
        if quiet is not None: self.quiet = quiet
        if debug is not None: self.debug = debug

    # Helper functions for printing messages, with colors
    # and nice wrapping
    def assistant_thought(self, thought):
        if self.quiet:
            return
        if thought is not None:
            self.console.print("\n[Assistant Thought]", style="blue bold")
            m = Markdown(thought, code_theme=self.THEME)
            self.console.print(m, width=self.WIDTH)
        else:
            self.console.print("\n[Assistant] NO THOUGHT!", style="blue bold")
        self._last = "ASSISTANT"
    def assistant_action(self, action):
        if self.quiet:
            return
        if action is not None:
            self.console.print("\n[Assistant Action]", style="dark_orange bold")
            m = Markdown(action, code_theme=self.THEME)
            self.console.print(m, width=self.WIDTH)
        else:
            self.console.print("\n[Assistant] NO ACTION!", style="dark_orange bold")
        self._last = "ASSISTANT"

    def observation_message(self, message):
        if self.quiet:
            return
        self.console.print("\n[Observation]", style="yellow bold")
        m = Markdown(message, code_theme=self.THEME)
        self.console.print(m, width=self.WIDTH)
        self._last = "OBSERVATION"

    def user_message(self, message):
        if self.quiet:
            return
        self.console.print("\n[User]", style="green bold")
        m = Markdown(message, code_theme=self.THEME)
        self.console.print(m, width=self.WIDTH)
        self._last = "USER"
            
    def system_message(self, message):
        if self.quiet:
            return
        self.console.print("[System Prompt]\n", style="red bold")
        m = Markdown(message, code_theme=self.THEME)
        self.console.print(m, width=self.WIDTH)
        self._last = "SYSTEM"

    def debug_message(self, message, truncate=False):
        self.debug_log.append(message)
        if self.debug:
            if self._last != "DEBUG": self.console.print()
            if truncate and len(message) > 100:
                message = message[:100].strip()
            self.console.print(f"DEBUG: {message}", style="dim")
            self._last = "DEBUG"

    def start_progress(self):
        """Start the status bar for progress updates"""
        self.progress = Status("PROGRESS: ...", console=self.console)
        self.progress.start()
    def stop_progress(self):
        """Stop the status bar for progress updates"""
        if self.progress is not None:
            self.progress.stop()

    def progress_message(self, message):
        # Do not quiet this
        if self.progress is not None:
            self.progress.update(f"PROGRESS: {message}")

    def print(self, *args, force=False, **kwargs):
        if not self.quiet or force:
            self.console.print(*args, **kwargs)

logger = Logger()
