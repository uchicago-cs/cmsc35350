# LLM-based article processing pipeline 

This repository contains text processing code relevant to the class CMSC 35360 at the University of Chicago. There are two directories:
* `source` is the code described in the following
* `eth` is example data relating to Ethylene, as referenced in the following

##  Some set up

Install *GNU parallel*: See https://www.gnu.org/software/parallel/parallel_tutorial.html

Install `txtai`:
```
% pip install txtai
% pip install "txtai[pipeline]"
```


## Assemble a list of keywords for your area of interest

You can do this with ChatGPT4 by using a prompt like the following, with my area of interest in boldface:

> I want to retrieve documents from Semantic Scholar that **relate to the science and engineering of materials that can catalyze the reduction of CO2 to ethylene**. Please suggest to me 100 sets of possible keywords. Output each set of keywords on a separate line, without any numbers.

Save the output from this prompt in a file `$DATASET/${DATASET}.txt`, where <DATASET> is a unique string like "eth" for Ethylene.

Edit the file to prepend '(  and append )' to each line, giving e.g.:
```
'( ethylene production from CO2 )'
'( CO2 reduction to ethylene catalysts )'
'( materials science CO2 conversion )'
...
```


## Retrieve titles and abstracts; eleminate duplicates

Run the program `get_papers.sh` which uses `get_papers.py` to query Semantic Scholar for titles + abstract that pertain to the keywords in the file that you just created. Provide <DATASET> as an argument:

```
% DATASET=eth
% cd source
% source get_papers.sh $DATASET
```

This produces a file `../$DATASET/{$DATASET}.jsonl` that contains information retrieved from Semantic Scholar (SS).
This file has one JSON document per line, with each document representing a paper, containing an SS id, title, abstract, etc.

Eliminate duplicates:

```
% sort -u ../$DATASET/$DATASET.jsonl > ../$DATASET/${DATASET}_uniq.jsonl
% mv ../$DATASET/${DATASET}_uniq.jsonl ../$DATASET/${DATASET}.jsonl
```


## Identify relevant documents

Your original queries likely generated many irrelevant documents.  For example, my queries relating to Ethylene returned articles relating to the ripening of fruit. Thus, you may want to use an LLM to rate the relevance of each paper found so far. The program `check_relevance.py` does this, using this prompt: 

>gpt_user_prompt = "Read the following abstract carefully. After reading, answer the following questions to determine if the abstract pertains to research related to finding a new and improved catalyst for the conversion of CO2 to ethylene, giving a score of 1 if true and 0 if false, and reporting each in a separate line with the form <HEADING>: <numeric score> <explanation>: **Topic Relevance**: Does the abstract mention 'CO2', 'carbon dioxide', 'ethylene', or 'catalysts'? List any terms used in the abstract that relate to these keywords.  **Research Focus**: Is the primary focus of the research on developing or testing materials that could act as catalysts? Specify what the research aims to achieve or discover.  **Outcome Mention**: Does the abstract discuss any results or potential outcomes regarding the efficiency, selectivity, or improvement of catalysts for converting CO2 to ethylene? Briefly describe these outcomes.  **Innovation Highlight**: Does the abstract indicate any novel approaches, techniques, or materials being investigated or used for the catalysts? Detail any innovative aspects mentioned. **Aggregate Score**: Add the four scores to get an aggregate score of from 0 to 4, and report that score in the form **Aggregate Score**: <score>, along with a sentence of about 50 words explaining your overall score. [## BEGIN ABSTRACT " + chunk + " END ABSTRACT ##]"

We run the program as follows:

```
% python check_relevance.py $DATASET
```
This produces a file `../$DATASET/${DATASET}_scores.csv`, e.g. see the first two lines of `eth/eth_scores.csv`:

```
000019fa6cd085dd4668e61800794e0764516e37,3,1,0,1,1,"The abstract is partially relevant to the topic of finding a new and improved catalyst for the conversion of CO2 to ethylene, as it discusses the use of TiO2 as a catalyst and the limitation of CO2 formation. However, the primary focus is on waste management and not specifically on CO2 to ethylene conversion."
00297f4d2ddee2de98c1d04a03529a349ddbff32,4,1,1,1,1,"The abstract is highly relevant to research on finding a new and improved catalyst for the conversion of CO2 to ethylene, as it discusses the development of novel MOFs with excellent catalytic activity in CO2 fixation, which is a crucial step towards converting CO2 to ethylene."
```

You can then identify the documents with different scores:
```
% grep ",4," ../$DATASET/${DATASET}_scores.csv > ../$DATASET/${DATASET}_score4.csv
% grep ",3," ../$DATASET/${DATASET}_scores.csv > ../$DATASET/${DATASET}_score3.csv
% grep ",2," ../$DATASET/${DATASET}_scores.csv > ../$DATASET/${DATASET}_score2.csv
% grep ",1," ../$DATASET/${DATASET}_scores.csv > ../$DATASET/${DATASET}_score1.csv
% grep ",0," ../$DATASET/${DATASET}_scores.csv > ../$DATASET/${DATASET}_score0.csv
```

# Extract document ids and retrieve documents

Now we are ready to retrieve documents. This requires a Semantic Scholar API key. You'll need to edit `download_from_ids.sh` to indicate which ids are to be fetched. E.g., you might use the followibg to fetch just the documents that were rated as highly relevant:

```
cat ../$DATAST/${DATASET}_score4.ids | parallel -j 1 "python3.12 simple.py -c $1 {}"
```

Here goes:

```
% export S2_API_KEY=$MY_SS_API_KEY
% source download_from_ids.sh $DATASET <NUMBER>
```

This produces a folder `../$DATASET/papers_${DATASET}` containing the retrieved papers.
Note it will only retrieve those with open source PDFs, which experience suggests to be around 10-15\% of all documents.


## Extract text from PDFs

We then use the `txtai` library to extract the txt from the PDFs:

```
% python extract_txt_from_pdf.py $DATASET
```

This produces, for each valid PDF, a file with a ".txt" extension in the folder `../$DATASET/papers_${DATASET}`.

Note: If you need to re-run this program, e.g., because of an error, you may want to search for the words "Substitute the following" in `extract_txt_from_pdf.py` and enter the name of a file containing SS ids that were reported in previous runs to be non-open access, just to speed things yp,


