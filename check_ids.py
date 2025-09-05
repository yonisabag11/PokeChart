import json

# Load the JSON data
with open('pokedex.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all IDs
ids = [int(k) for k in data.keys()]
ids_set = set(ids)

print(f"Min ID: {min(ids)}, Max ID: {max(ids)}, Total: {len(ids)}")

# Check the excluded IDs
excluded = [221, 824, 916, 925, 931, 964, 978, 982]
print("\nChecking excluded IDs:")
for pid in excluded:
    exists = pid in ids_set
    print(f"ID {pid}: {'EXISTS' if exists else 'MISSING'}")

# Find gaps in the sequence
gaps = []
for i in range(1, max(ids) + 1):
    if i not in ids_set:
        gaps.append(i)

print(f"\nTotal missing IDs in range 1-{max(ids)}: {len(gaps)}")
print(f"First 20 missing IDs: {gaps[:20]}")

# Check if our excluded IDs are in the gaps
excluded_in_gaps = [pid for pid in excluded if pid in gaps]
print(f"\nExcluded IDs that are actually missing from JSON: {excluded_in_gaps}")
