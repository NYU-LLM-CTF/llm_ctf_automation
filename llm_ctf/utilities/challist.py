import csv
import os
from pathlib import Path

file_path = Path(__file__).resolve()

class ChalNotFoundError(Exception):
    def __init__(self, chalname="Unknown Challenge", code=404):
        super().__init__(f"Challenge {chalname} Not Found, Skip")
        self.code = code

class ChallengeList:
    def __init__(self, challist=os.path.join(file_path.parent, 'challenge_list.tsv')) -> None: 
        # Challenge information for tracking the challenges
        self.chal_info = []
        # Challenge name for actual usage
        self.chal_names = []
        with open(challist, 'r', newline='') as file:
            tsv_reader = csv.reader(file, delimiter='\t')
            for row in tsv_reader:
                self.chal_info.append(row)
                self.chal_names.append(row[3])
                
    def find_chal(self, chalname):
        if chalname not in self.chal_names:
            raise ChalNotFoundError(chalname=chalname)
        
    
    
if __name__ == "__main__":
    cl = ChallengeList()
    try:
        cl.find_chal("unlimitsed_subway")
        cl.find_chal("unlimited_subway")
    except ChalNotFoundError as e:
        print(e)