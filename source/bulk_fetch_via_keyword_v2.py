import requests
import json
import sys
import time
from pathlib import Path

if len(sys.argv) != 4:
    print("Usage: python bulk_fetch_via_keyword.py 'search_term' year filename")
    sys.exit(1)

query = sys.argv[1]
year = sys.argv[2]
outfile = sys.argv[3]

print(f'Query = {query}; year = {year}')

#query = '(cold -temperature) | flu'

fields = 'abstract,title,year'

url = f'http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year={year}'
r = requests.get(url).json()

try:
    print(f"  Will retrieve an estimated {r['total']} documents")
except:
    print(f"  Retrieval failed")
    exit(1)

retrieved = 0

directory_path = Path(f'{outfile}')
if not directory_path.exists():
    directory_path.mkdir(parents=True, exist_ok=True)

with open(f'../{outfile}/{outfile}.jsonl', 'a') as file:
    while True:
        if 'data' in r:
            retrieved += len(r['data'])
            for paper in r['data']:
                print(json.dumps(paper), file=file)
        if 'token' not in r:
            break
        r = requests.get(f"{url}&token={r['token']}").json()

print(f'  Retrieved {retrieved} papers total')
time.sleep(1)
