import json
import sys

if len(sys.argv) != 2:
    print("Usage: python extract_ids_from_jsonl.py 'prefix'")
    sys.exit(1)

prefix = sys.argv[1]

print(f'Extracting document ids from {prefix}/{prefix}.jsonl')

file_path = f'../{prefix}/{prefix}.jsonl'

# List to hold all extracted ids
ids = []

# Open the file and read line by line
try:
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Parse the JSON line into a dictionary
                data = json.loads(line)
                # Extract the 'id' field
                if 'paperId' in data:
                    ids.append(data['paperId'])
                else:
                    print("No 'id' field found in this record.")
            except json.JSONDecodeError:
                print("Error decoding JSON.")
except FileNotFoundError:
    print("File not found.")

# Optionally print or process the list of ids
unique_ids = set(ids)
print(f'Found {len(unique_ids)} unique ids from {len(ids)} documents')
print(f'Writing ids to {prefix}/{prefix}.ids')

with open(f'../{prefix}/{prefix}.ids', 'w') as file:
    # Iterate through each item in the list
    for item in unique_ids:
        # Write each item on a new line
        file.write(item + '\n')
