import yaml

class PromptManager:
    """Handles formatting of the prompts"""
    def __init__(self, promptyaml, challenge, environment):
        
        with open(promptyaml, "r") as c:
            self.templates = yaml.safe_load(c)
        self.challenge = challenge
        self.environment = environment

        # FIXME need to hotplug server description
        if challenge.server_type == "web":
            self.server_description = self.get("web_server_description")
        elif challenge.server_type == "nc":
            self.server_description = self.get("nc_server_description")
        else:
            self.server_description = ""

    def get(self, key, **kwargs):
        # TODO check if templating done properly
        tmpl = self.templates.get(key, "")
        prompt = tmpl.format(challenge=self.challenge, environment=self.environment, 
                             prompter=self, **kwargs)
        return prompt
