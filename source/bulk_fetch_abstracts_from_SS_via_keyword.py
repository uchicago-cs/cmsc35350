#!/usr/bin/env python3

import requests
import random
import json
import sys
import time
from pathlib import Path
import argparse

max_attempts = 3
max_pause    = 5

def attempt_to_retrieve(url):
    for attempt in range(max_attempts):
        try:
            print('Attempt', url)
            r = requests.get(url).json()
            print(f"  Will retrieve an estimated {r['total']} documents")
            return r
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_attempts - 1:
                pause_time = random.uniform(0, max_pause) + 1
                print(f"Pausing for {pause_time:.2f} seconds...")
                time.sleep(pause_time)
            else:
                print("All attempts failed.")
                return Null


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', '-d', type=str, required=True)
    parser.add_argument('--file',    '-f', type=str)
    parser.add_argument('--query',   '-q', type=str)
    parser.add_argument('--year',    '-y', type=str)
    args = parser.parse_args()

    dataset = args.dataset

    if args.year == None:
        years = range(2016,2025)
    else:
        years = [args.year]

    if args.query == None and args.file == None:
        print('Need query or query file')
        exit(1)
    if args.query != None and args.file != None:
        print('Cannot have both query and query file')
        exit(1)

    if args.query != None:
        queries = [args.query]
    else:
        # Open file containing a list of search terms
        with open(args.file, 'r') as file:
            queries = file.readlines()
            queries = [q.strip() for q in queries]  #

    fields = 'abstract,title,year'

    # Create <dataset> directory if it does not already exist
    directory_path = Path(f'{dataset}')
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)

    retrieved = 0
    with open(f'{dataset}/{dataset}.jsonl', 'a+') as file:
        for query in queries:
            for year in years:
                url = f'http://api.semanticscholar.org/graph/v1/paper/search/bulk?query={query}&fields={fields}&year={year}'
                while True:
                    r = attempt_to_retrieve(url)
                    print(r)
                    if 'data' in r:
                        retrieved += len(r['data'])
                        for paper in r['data']:
                            print(json.dumps(paper), file=file)
                    if 'token' not in r:
                        break
                    r = requests.get(f"{url}&token={r['token']}").json()
                    time.sleep(1)

