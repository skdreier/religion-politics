#!/usr/bin/env bash

# Sample usage:
# bash get_filtered_religious_files.sh /religious/input/dir/path sample_output_dir/

if [ "$#" -ne 2 ]
then
	echo "Usage: $1 <LATEST_RELIGIOUS_INPUT_DIR> $2 <LATEST_FILTERED_OUTPUT_DIR>
	exit 1
fi

inputdir=$1
outputdir=$2

python make_pig_script_from_template.py filtered_religious_files None

pig -p LATEST_RELIGIOUS_INPUT_DIR=$inputdir -p LATEST_FILTERED_OUTPUT_DIR=$outputdir get_filtered_religious_files.pig
