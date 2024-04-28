import os
import sys
import time
import openai

port = 80

if len(sys.argv) != 3:
    print("Usage: python llm_query.py <file_path> <request_type>")
    sys.exit(1)

# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = f"http://195.88.24.64:{port}/v1"

file_path = sys.argv[1]
request_type = sys.argv[2]

def create_prompt(request_type, chunk, previous_response):
    if request_type == 'summarize':
        if previous_response=='':
            gpt_user_prompt = "Please summarize in approximately 800 words this paper. [## BEGIN PAPER " + chunk + " END PAPER  ##] Your summary should contain the TITLE of the paper, the YEAR the paper was published, the KEY FINDINGS, the MAIN RESULT, any HYPOTHESES the paper proposes or that you can infer from the text when the hypothesis is not explict. Please propose EXPERIMENTS that would validate the hypothesis. In addition to generating the summary, please generate a list of up to ten KEYWORDS that are relevant to the paper.  Please include these UPPER CASE words as headings in your response."
        else:
            gpt_user_prompt = "We previously asked you summarize a paper in approximately 800 words and you provided this summary: [## BEGIN SUMMARY " + previous_response + " END SUMMARY ##]. Based on the following additional content, please UPDATE your response (i.e., edit it, rather than append to it) under each heading, if needed: [## BEGIN PAPER " + chunk + " END PAPER  ##]. Do not mention that you are updating. Remember to keep the summary to about 800 words."
    else:
        print('Bad request type:', request_type)
        exit(1)
    return (gpt_user_prompt)


client = openai.OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Read the entire content of the file
with open(file_path, 'r', encoding='utf-8') as file:
    file_contents = file.read()

CHUNK_SIZE = 2000

num_chunks = int(len(file_contents)/CHUNK_SIZE) + 1

print(f'File {file_path} contains {len(file_contents)} bytes in {num_chunks} chunks of size at most {CHUNK_SIZE}\n')

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
            #print(response.choices[0].message.content)
            break
        except:
            print("Hypo trying again port "+str(port))
            retry_count += 1
            time.sleep(2)
            if retry_count == max_retries:
                print("Maximum retries reached. Exiting the program.")
                exit
    time.sleep(2)


# Try first chunk
chunk = file_contents[:CHUNK_SIZE]
gpt_user_prompt = create_prompt(request_type, chunk, '')
response = query_llm(gpt_user_prompt)

print(f'========== RESPONSE #1 ==========================================\n{response}')


"""
# See if later chunks improve things
for i in range(num_chunks-1):
    chunk = file_contents[CHUNK_SIZE*(i+1):CHUNK_SIZE*(i+2)]
    
    gpt_user_prompt = create_prompt(request_type, chunk, response)
    response = query_llm(gpt_user_prompt)
    print(f'---------- RESPONSE #{i+2} ---------------------------------------\n{response}')
"""

base = os.path.splitext(file_path)[0]
outfile = f'{base}.summary'

print('Writing LLM response to', outfile)

with open(outfile, 'w') as file:
    file.write(response)
    file.write('\n')
