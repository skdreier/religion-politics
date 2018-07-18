#!/bin/bash

I_PARSED_DATA_DIR=/dataset-derived/gov/parsed/arcs
O_DATA_DIR=/user/lucylin/arcs

I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum

PIG_SCRIPT=FilterFiles.pig

# hdfs -ls returns in this format:
#   drwxr-xr-x   - vinay supergroup
#       0 2014-04-13 08:04 /dataset-derived/gov/parsed/arcs/bucket-0
# there is the -C option to just get the path... except that the option was
#   introduced in 2.8+. the cluster has 2.7.3.
# so instead (via https://stackoverflow.com/a/21574829):
I_PARSED_DATA_LIST=`hdfs dfs -ls $I_PARSED_DATA_DIR \
    | sed 1d \
    | perl -wlne'print +(split " ",$_,8)[7]'`

for I_PARSED_DATA in $I_PARSED_DATA_LIST
do
    echo "Input: $I_PARSED_DATA"

    pig -p $I_PARSED_DATA \
        -p $I_CHECKSUM_DATA \
        -p $O_DATA_DIR \
        $PIG_SCRIPT
done
