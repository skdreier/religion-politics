#!/usr/bin/env bash

if [ "$#" -ne 5 ]
then
	echo "Usage: $1 <window size around search term> $2 <# top results to collect> $3 <local prefix of output dir> $4 <I_PARSED_DATA> $5 <I_CHECKSUM_DATA>"
	exit 1
fi

source add_dependencies_to_classpath.sh  # just in case this hasn't been done yet

windowsize=$1
numresultstocollect=$2
outputdirprefix=$3

python make_get_cooccurrence_words_script.py $windowsize $numresultstocollect $outputdirprefix $5

pig -p I_PARSED_DATA=$4 -p I_CHECKSUM_DATA=$5 get_cooccurrence_words.pig
