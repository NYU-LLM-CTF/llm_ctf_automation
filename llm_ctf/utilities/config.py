import json
from pathlib import Path

class Config:
    def __init__(self, config_path) -> None:
        self.config_path = config_path
        self.config = self.setup()
        
    def setup(self):
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        return config
    
    def get_max_token(self, model):
        return self.config[model]["max_token"]
    

if __name__ == "__main__":
    config_dir = Path(__file__).parent.parent.parent.joinpath("config")
    config = Config(config_dir.joinpath("config_gpt.json"))
    print(config.get_max_token("gpt-4-turbo-preview"))