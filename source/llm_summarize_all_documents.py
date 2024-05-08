import os
import glob
import sys
import time
import openai

port = 80

if len(sys.argv) != 4:
    print('Usage: python3.11 sourcce/llm_summarize_all_documents.py <dataset> <ip_address> <api_key>')
    exit(1)

dataset    = sys.argv[1]
ip_address = sys.argv[2]
api_key    = sys,argv[3]


# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = api_key
openai_api_base = f"http://{ip_address}:{port}/v1"


def create_prompt(chunk):
    gpt_user_prompt = "Please summarize in approximately 800 words this paper. [## BEGIN PAPER " + chunk + " END PAPER  ##] Your summary should contain the TITLE of the paper, the YEAR the paper was published, the KEY FINDINGS, the MAIN RESULT, one novel HYPOTHESIS the paper proposes or that you can infer from the text when the hypothesis is not explicit. Please propose an EXPERIMENT that would validate the hypothesis; be specific about required equipment and steps to follow. In addition to generating the summary, please generate a list of up to ten KEYWORDS that are relevant to the paper.  Please output your response as a valid JSON document with the UPPER CASE words as keys, and no other text before or after the JSON document."
    return (gpt_user_prompt)


client = openai.OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

gpt_assistant_prompt = "You are a super smart AI that knows about science. You follow directions and you are always truthful and concise in your reponses."

def query_llm(gpt_user_prompt):
    message=[{"role": "assistant", "content": gpt_assistant_prompt}, {"role": "user", "content": gpt_user_prompt}]
    #print(message)
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
            #time.sleep(2)
            return(response.choices[0].message.content)
            break
        except Exception as e:
            print('Exception', e)
            print("Hypo trying again port "+str(port))
            retry_count += 1
            time.sleep(1)
            if retry_count == max_retries:
                print("Maximum retries reached. Giving up")
                return None
    time.sleep(2)

def generate_summary(index, infile, outfile):

    # Read the entire content of the file
    with open(infile, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    CHUNK_SIZE = 20000

    num_chunks = int(len(file_contents)/CHUNK_SIZE) + 1

    print(f'{index:>4d} Reading {infile}') # contains {len(file_contents)} bytes in {num_chunks} chunks of size at most {CHUNK_SIZE}')

    # Try first chunk
    chunk = file_contents[:CHUNK_SIZE]
    gpt_user_prompt = create_prompt(chunk)
    response = query_llm(gpt_user_prompt)
    if response == None:
        print('No response')
        return

    print('       Writing LLM response to', outfile)

    with open(outfile, 'w') as file:
        file.write(response)
        file.write('\n')


for index, file in enumerate( glob.glob(f'{dataset}/papers/*.txt') ):
    summary_file = os.path.splitext(file)[0]+'.summary'
    if os.path.isfile(summary_file) and os.path.getsize(summary_file) > 0:
        print(f'{index:>4d} Skipping {summary_file}')
        continue
    generate_summary(index, file, summary_file)
  
