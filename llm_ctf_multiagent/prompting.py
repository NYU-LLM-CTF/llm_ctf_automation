import yaml

class PromptManager:
    """Handles formatting of the prompts"""
    def __init__(self, promptyaml, challenge, environment):
        
        with open(promptyaml, "r") as c:
            self.templates = yaml.safe_load(c)
        self.challenge = challenge
        self.environment = environment

    def get(self, key, **kwargs):
        # TODO check if templating done properly
        tmpl = self.templates.get(key, "")
        prompt = tmpl.format(challenge=self.challenge, environment=self.environment, **kwargs)
        return prompt
