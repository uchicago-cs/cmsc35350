import requests
import random
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

fields = 'abstract,title,year'

url = f'http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year={year}'

max_attempts = 3                                                                                                                        
max_pause = 5                                                                                                                           
for attempt in range(max_attempts):                                                                                                     
    try:
        r = requests.get(url).json()
        print(f"  Will retrieve an estimated {r['total']} documents")
        break                                                                                                                        
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        if attempt < max_attempts - 1:
            pause_time = random.uniform(0, max_pause)
            print(f"Pausing for {pause_time:.2f} seconds...")
            time.sleep(pause_time)
        else:
            print("All attempts failed.")
            exit(1)

retrieved = 0

directory_path = Path(f'{outfile}')
if not directory_path.exists():
    directory_path.mkdir(parents=True, exist_ok=True)

with open(f'{outfile}/{outfile}.jsonl', 'a') as file:
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
