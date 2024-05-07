#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Missing argument: <project>"
else
    for file in $1/papers/*.summary; do
        echo Compacting $file
        tr '\n' ' ' < $file | sed 's/  */ /g' > $file.2
    done
fi
