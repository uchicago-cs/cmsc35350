import glob
from pathlib import Path
import json
import sys

if len(sys.argv) != 2:
    print('Usage: python generate_jsonl_summary_file.py <DATASET>')
    exit(1)

dataset   = sys.argv[1]
outfile = f'{dataset}/all.jsonl'

# Fix various dumb LLM errors
def clean_up(line):
    line = line.replace("Here is the summary of the paper in JSON format: ```", '')
    line = line.replace("```", '')
    line = line.replace("20xx", '"20xx"')
    line = line.replace("Let me know if you have any further requests!",'')
    line = line.replace("Note: The title and year of the paper are not explicitly provided, so I generated a title based on the keywords and assumed a recent publication year.", '')
    if line[-2:-1] != '}':
        line += '}'
    return(line)

with open(outfile, 'w') as file:
    for infile in glob.glob(f'{dataset}/papers/*.2'):
        paper_id = Path(infile).stem.split('.')[0]
        with open(infile, 'r', encoding='utf-8') as reader:
            file_contents = reader.read()
        if file_contents != '':
            file_contents = clean_up(file_contents)
            try:
                data = json.loads(file_contents)
                data['ID'] = paper_id
                data = json.dumps(data)
                file.write(data)
                file.write('\n')
            except:
                print('Skipping', paper_id)
