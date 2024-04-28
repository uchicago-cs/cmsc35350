#!/bin/bash

if [ $# != 1 ]; then
    echo "Argument needed: Name of input file"
    return
fi

echo "Reading $1/$1.txt, writing $1/$1.jsonl"

rm -f $1/$1.jsonl
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2016 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2017 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2018 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2019 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2020 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2021 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2022 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2023 $1"
cat $1/$1.txt | parallel -j 1 "python bulk_fetch_via_keyword.py {}	2024 $1"
