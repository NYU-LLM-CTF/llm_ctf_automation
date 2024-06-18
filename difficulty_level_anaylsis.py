import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

dicts_finals = defaultdict(int)
dict_quals = defaultdict(int)

def find_json_fields(directory):
    chal_missing = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'challenge.json':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                        initial = data.get('initial')
                        
                        point = data.get('points')
                        name = data.get('name')
                        # print(f"File: {file_path}")
                        # if initial is not None:
                        #     if "Quals" in file_path:
                        #         dict_quals[int(initial)] += 1
                        #     else:
                        #         dicts_finals[int(initial)] += 1
                        #     print(f"  Initial: {initial}")
                        if point is not None:
                            if "Quals" in file_path:
                                dict_quals[int(point)] += 1
                            else:
                                dicts_finals[int(point)] += 1
                            print(f"  Point: {point}")
                        else:
                            chal_missing += 1
                except Exception as e:
                    # print(e)
                    pass
                    
    print(chal_missing)

find_json_fields('LLM_CTF_Database')
# Sort the keys and align the counts
categories_quals = sorted(dict_quals.keys())
counts_quals = [dict_quals[key] for key in categories_quals]

categories_finals = sorted(dicts_finals.keys())
counts_finals = [dicts_finals[key] for key in categories_finals]

# Create figure and axes for two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))  # 1 row, 2 columns, adjusted figure size

# Constants for plotting
width = 0.8  # the width of the bars

# Plot Quals data
ind_quals = np.arange(len(categories_quals))
ax1.bar(ind_quals, counts_quals, width, label='Quals', color='darkcyan')
ax1.set_xlabel('Difficulties (Points assigned)')
ax1.set_ylabel('Number of Challenges')
ax1.set_title('Quals Histogram of CTF Challenges by Difficulty')
ax1.set_xticks(ind_quals)
ax1.set_xticklabels(categories_quals, rotation=45)
ax1.legend()

# Plot Finals data
ind_finals = np.arange(len(categories_finals))
ax2.bar(ind_finals, counts_finals, width, label='Finals', color='firebrick')
ax2.set_xlabel('Difficulties (Points assigned)')
ax2.set_ylabel('Number of Challenges')
ax2.set_title('Finals Histogram of CTF Challenges by Difficulty')
ax2.set_xticks(ind_finals)
ax2.set_xticklabels(categories_finals, rotation=45)
ax2.legend()

# Layout adjustments
plt.tight_layout()
plt.savefig("difficulty_histogram_subplots.png")
plt.show()