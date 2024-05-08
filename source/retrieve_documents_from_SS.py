#!/usr/bin/env python3
#import dotenv
#dotenv.load_dotenv()

import argparse
import os
import requests
from requests import Session
from typing import Generator, Union
from time import sleep

import urllib3
urllib3.disable_warnings()

S2_API_KEY = os.environ['S2_API_KEY']

ids = []
# Substitute the following with a list of known non-open access ids, as reported from a previous run, to accelerate things
# if you are running more than once
#with open('RNA/RNA/RNA.ids', 'r') as file:
#    ids = file.readlines()
#    ids = [id.strip() for id in ids]  #

def get_paper(paper_id: str, fields: str = 'paperId,title', **kwargs) -> dict:
    params = {
        'fields': fields,
        **kwargs,
    }
    headers = {
        'X-API-KEY': S2_API_KEY,
    }

    with requests.get(f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}', params=params, headers=headers) as response:
        response.raise_for_status()
        return response.json()


def download_pdf(url: str, path: str, user_agent: str = 'requests/2.0.0'):
    # send a user-agent to avoid server error
    headers = {
        'user-agent': user_agent,
    }

    # stream the response to avoid downloading the entire file into memory
    with requests.get(url, headers=headers, stream=True, verify=False) as response:
        # check if the request was successful
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print('Error', e, url)
            raise  # Optionally re-raise the exception after logging it

        if response.headers['content-type'] != 'application/pdf':
            print('Error not a PDF:', url)
            raise Exception('The response is not a pdf')

        with open(path, 'wb') as f:
            # write the response to the file, chunk_size bytes at a time
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_paper(paper_id, collection, user_agent):
    # Check if not open access
    if paper_id in ids:
        return 'Already known'
    # check if the pdf has already been downloaded
    pdf_path = os.path.join(f'{collection}/papers', f'{paper_id}.pdf')
    if os.path.exists(pdf_path):
        print('SHOULD NOT GET HERE')
        exit(1)
        return pdf_path

    sleep(1)

    try:
        paper = get_paper(paper_id, fields='paperId,isOpenAccess,openAccessPdf')
    except requests.exceptions.HTTPError as e:
        print(e)
        print(f"Failed to download {paper_id}: HTTP Error:", e.response.text)
        return 'Failed to download paper'

    # check if the paper is open access
    if not paper['isOpenAccess']:
        return 'Not open access'

    paperId: str = paper['paperId']
    if paper['openAccessPdf']==None:
        return('Not open access PDF')
    pdf_url: str = paper['openAccessPdf']['url']
    pdf_path = os.path.join(f'{collection}/papers', f'{paperId}.pdf')

    # create the directory if it doesn't exist
    os.makedirs(collection, exist_ok=True)

    # check if the pdf has already been downloaded
    if os.path.exists(pdf_path):
        print('SHOULD NOT GET HERE')
        exit(1)

    try:
        download_pdf(pdf_url, pdf_path, user_agent=user_agent)
    except:
        return(f'Download failed: {pdf_path}')

    return pdf_path


def main(args: argparse.Namespace) -> None:
    collection = args.collection
    with open(args.paper_ids, 'r') as file:
        paper_ids = file.readlines()
        paper_ids = [id.strip() for id in paper_ids]  #

    # Skip specified number
    count = int(args.number)
    paper_ids = paper_ids[count:]

    if not os.path.exists(f'{collection}/papers'):
        os.makedirs(f'{collection}/papers')

    for paper_id in paper_ids:
        if os.path.exists(f'{collection}/papers/{paper_id}.pdf'):
            #print(f'[{count:>5}] {paper_id} already exists')
            pass
        else:
            result = download_paper(paper_id, collection=args.collection, user_agent=args.user_agent)
            if result=='Not open access':
                print(f'[{count:>5}] {paper_id} is not open access') 
            elif result=='Not open access PDF':
                print(f'[{count:>5}] {paper_id} has no open access PDF')
            elif result=='Failed to download paper':
                print(f'[{count:>5}] {paper_id} failed to download')
            elif result=='Download failed':
                print(f'[{count:>5}] {paper_id} failed to download 2')
            elif result=='Already known':
                # Skipping as already known to be not open access
                pass
            else:
                print(f'[{count:>5}] {paper_id} downloaded to to {result}')
        count += 1


# "Collection" is the dataset
# "Number" is number to skip (default 0)
# "paper_ids" is list to try
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collection', '-c')
    parser.add_argument('--number', '-n', default=0)
    parser.add_argument('--user-agent', '-u', default='requests/2.0.0')
    parser.add_argument('--paper_ids', '-p')
    args = parser.parse_args()
    main(args)
