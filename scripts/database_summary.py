import os
import json
from dataclasses import dataclass

chalist = []

@dataclass
class ChalMeta:
    year: str
    event: str
    chalname: str
    category: str
    description: str
    
    def to_dict(self):
        return {"year": self.year, "event": self.event, "category": self.category, "name": self.chalname, "description": self.description}

def find_challenge_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'challenge.json':
                chalist.append(os.path.join(root, file))
                
def parse_chal(chalist: list):
    chal_metadata = []
    for chal in chalist:
        try:
            with open(chal, 'r') as f:
                pathinfo = chal.split('/')
                year, event, category, name = pathinfo[2], pathinfo[3], pathinfo[4], pathinfo[5]
                chalinfo = json.load(f)
                chal_metadata.append(ChalMeta(year=year, event=event, category=category, chalname=name, description=chalinfo["description"]))
        except:
            print(f"{chal} found as a soft link, skip!")
    return list(map(lambda x: x.to_dict(), chal_metadata))
            
def log_output(chalmeta):
    json_data = json.dumps(chalmeta, indent=4)
    with open('./chal_data.json', 'w') as file:
        file.write(json_data)

if __name__ == "__main__":
    directory = './LLM_CTF_Database/'
    find_challenge_json_files(directory)
    chal_meta = parse_chal(chalist)
    # print(chal_meta)
    log_output(chal_meta)
