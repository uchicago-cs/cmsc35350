import json
import sys

if len(sys.argv) != 2:
    print('Usage: python3.11 source/extract_hypotheses_from_llm_output.py <dataset>')
    sys.exit(1)

dataset = sys.argv[1]

data = []
with open(f"{dataset}/all.jsonl",'r',encoding='utf-8') as reader:
   for line in reader:
       data.append(json.loads(line))

hypotheses = []
for entry in data:
    try:
        hyp = entry['HYPOTHESIS']
        id  = entry['ID']
        expt= entry['EXPERIMENT']
        hypotheses += [(id, hyp, expt)]
    except:
        print('ERROR:', entry)

for h in hypotheses:
    print(h)

print(f'A total of {len(hypotheses)} hypotheses extracted')
