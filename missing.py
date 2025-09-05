import json

with open('pokedex.json') as f:
    dex = json.load(f)

all_ids = set(str(i) for i in range(1, 1026))
present_ids = set(dex.keys())
missing_ids = sorted(all_ids - present_ids)
print(missing_ids)