#
if [ $# != 2 ]; then
    echo "Argument needed: '<STRING>' 'number of papers to try'"
    return
fi

echo "Reading $1/$1.ids, writing to $1/papers"

#cat $1/$1.ids | head -n $2 | parallel -j 1 "python3.12 simple.py -c $1 {}"
cat ../eth/eth_score3.ids | parallel -j 1 "python3.12 simple.py -c $1 {}"
#cat RNA/RNA/RNA.ids | parallel -j 1 "python3.12 simple.py -c $1 {}"
