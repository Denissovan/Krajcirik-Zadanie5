#!/bin/bash

directory=$(ls $1*)

logfile=$2

echo $directory

# list all files in dumps directory
for file in $directory
do
    echo Processing file: $file
    for attempt in {1..7}
        do
            # bulk import the file and see if the attempt was succesful
            err=$(curl -sH "Content-Type: application/x-ndjson" -XPOST 'localhost:9200/tweets/_bulk' --data-binary @$file)
            # echo $err
            errs=$(echo $err | jq .errors)
            # echo $errs
            if [[ $errs == false ]];
                then
                    break
            fi
        done
    if [[ $errs == true ]];
        then 
            # echo "$err" | jq
            echo "$err" >> logfile
            echo Error ocured at file: $file, content: $file >> logfile
    fi
    echo Finished processing file: $file
done