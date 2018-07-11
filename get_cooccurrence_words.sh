#!/usr/bin/env bash

if [ "$#" -ne 5 ]
then
	echo "Usage: $1 <window size around search term> $2 <# top results to collect> $3 <local prefix of output dir> $4 <I_PARSED_DATA> $5 <I_CHECKSUM_DATA>"
	exit 1
fi

windowsize=$1
numresultstocollect=$2
outputdirprefix=$3

python3 make_get_cooccurrence_words_script.py $windowsize $numresultstocollect $outputdirprefix

pig -p I_PARSED_DATA=$3 -p I_CHECKSUM_DATA=$4 get_cooccurrence_words.pig
