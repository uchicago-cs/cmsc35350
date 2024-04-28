#
DATASET=eth
cat ../$DATASET/${DATASET}_uniq.jsonl | parallel --pipe -N 1 -j 10 python3 check_relevance_one.py output_{#}.txt
