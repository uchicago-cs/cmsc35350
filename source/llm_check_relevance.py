import os
import sys
import time
import openai
import json
import re
import csv

port = 80

if len(sys.argv) != 4:
    print("Usage: python check_relevance.py <server_ip> <api_key> <DATASET>")
    sys.exit(1)

server_ip = sys.argv[1]
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = sys.argv[2]
openai_api_base = f"http://{server_ip}:{port}/v1"
dataset = sys.argv[3]

def create_prompt(chunk):
    gpt_user_prompt = "Read the following abstract carefully. After reading, answer the following questions to determine if the abstract pertains to research related to finding a new and improved catalyst for the conversion of CO2 to ethylene, giving a score of 1 if true and 0 if false, and reporting each in a separate line with the form <HEADING>: <numeric score> <explanation>: **Topic Relevance**: Does the abstract mention 'CO2', 'carbon dioxide', 'ethylene', or 'catalysts'? List any terms used in the abstract that relate to these keywords.  **Research Focus**: Is the primary focus of the research on developing or testing materials that could act as catalysts? Specify what the research aims to achieve or discover.  **Outcome Mention**: Does the abstract discuss any results or potential outcomes regarding the efficiency, selectivity, or improvement of catalysts for converting CO2 to ethylene? Briefly describe these outcomes.  **Innovation Highlight**: Does the abstract indicate any novel approaches, techniques, or materials being investigated or used for the catalysts? Detail any innovative aspects mentioned. **Aggregate Score**: Add the four scores to get an aggregate score of from 0 to 4, and report that score in the form **Aggregate Score**: <score>, along with a sentence of about 50 words explaining your overall score. [## BEGIN ABSTRACT " + chunk + " END ABSTRACT ##]"
    return (gpt_user_prompt)

client = openai.OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

gpt_assistant_prompt = "You are a super smart AI that knows about science. You follow directions and you are always truthful and concise in your reponses."

def query_llm(gpt_user_prompt):
    message=[{"role": "assistant", "content": gpt_assistant_prompt}, {"role": "user", "content": gpt_user_prompt}]
    temperature=0.0
    frequency_penalty=0.0
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                    model='meta-llama/Meta-Llama-3-70B-Instruct',
                    messages = message,
                    temperature=temperature,
                    frequency_penalty=frequency_penalty
            )   
            time.sleep(2)
            return(response.choices[0].message.content)
            break
        except:
            print("Hypo trying again port "+str(port))
            retry_count += 1
            time.sleep(2)
            if retry_count == max_retries:
                print("Maximum retries reached. Exiting the program.")
                exit
    time.sleep(2)


def extract_scores(paperId, message):
    # Regular expression to find the scores and the summary sentence
    scores = re.findall(r'\*\*[^:]+\*\*: (\d)', message)
    try:
        final_sentence = re.search(r'\*\*Aggregate Score\*\*: \d\n(.+)', message).group(1)
    except:
        final_sentence = ''

    # Form the tuple as specified
    try:
        summary_tuple = (paperId, scores[4], scores[0], scores[1], scores[2], scores[3], final_sentence)
        return(summary_tuple)
    except:
        print('FAIL', paperId, scores, final_sentence)
        return ''


in_path  = f'{dataset}/{dataset}.jsonl'
out_path = f'{dataset}/{dataset}_scores.csv'

# Find what we already have
with open(out_path, 'r') as in_file:
    csv_reader = csv.reader(in_file)
    ids_already_read = []
    for row in csv_reader:
        if row:  # Check if row is not empty
            ids_already_read.append(row[0])

print('Already read:', ids_already_read)

count = 0

with open(out_path, 'a') as out_file:
    writer = csv.writer(out_file)
    with open(in_path, 'r' ) as in_file:
        for line in in_file:
            count += 1
            try:
                # Parse the JSON line into a dictionary
                json_data = json.loads(line)

                paperId = json_data['paperId']
                if paperId in ids_already_read:
                    print(f'[{count:>5}] Already seen: {paperId}')
                    continue

                title = json_data['title']
                abstract = json_data['abstract']
                if abstract == None:
                    print(f'[{count:>5}] No abstract: {paperId}')
                    continue

                print(f'\n[{count:>5}] PAPER {paperId}:\n\t{title}\n\t{abstract}')

                gpt_user_prompt = create_prompt(title + abstract)
                response = query_llm(gpt_user_prompt)
                response = response.replace("\n\n", "\n")
                #print(response)
                summary_tuple = extract_scores(paperId, response)
                if summary_tuple != '':
                    print(summary_tuple)
                    writer.writerow(summary_tuple)
            except json.JSONDecodeError:
                print("Error decoding JSON from line:", line)
    
