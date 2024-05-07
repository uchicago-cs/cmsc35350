import glob
from pathlib import Path
import json

project   = sys.argv[1]

# Fix various dumb LLM errors
def clean_up(count, line):
    #print('LINE', count, line)
    line = line.replace("Here is the summary of the paper in JSON format: ```", '')
    line = line.replace("```", '')
    line = line.replace("20xx", '"20xx"')
    line = line.replace("Let me know if you have any further requests!",'')
    line = line.replace("Note: The title and year of the paper are not explicitly provided, so I generated a title based on the keywords and assumed a recent publication year.", '')
    #print('LINE 2', count, line)
    if line[-2:-1] != '}':
        line += '}'
    return(line)


outfile = f'{project}/all.jsonl'

count = 0
with open(outfile, 'w') as file:
    for infile in glob.glob(f'{project}/papers/*.2'):
        count += 1
        paper_id = Path(infile).stem.split('.')[0]
        with open(infile, 'r', encoding='utf-8') as reader:
            file_contents = reader.read()
        if file_contents != '':
            file_contents = clean_up(count, file_contents)
            try:
                data = json.loads(file_contents)
                data['ID'] = paper_id
                data = json.dumps(data)
                file.write(data)
                file.write('\n')
            except:
                print('Skipping', paper_id)
              
