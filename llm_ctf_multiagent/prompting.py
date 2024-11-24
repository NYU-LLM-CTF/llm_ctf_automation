class PromptManager:
    """Handles formatting of the prompts"""
    def __init__(self, challenge, templates):
        self.challenge = challenge
        self.templates = templates

    def get(self, p):
        if p not in self.templates:
            return None
        # TODO do some templating
        return self.templates[p]
