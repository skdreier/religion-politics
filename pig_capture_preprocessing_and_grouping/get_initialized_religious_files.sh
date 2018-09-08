#!/usr/bin/env bash

# Sample usage:
# bash get_filtered_religious_files.sh /all/preprocessed/captures/path sample_output_dir/

if [ "$#" -ne 2 ]
then
	echo "Usage: $1 <ALL_PREPROCESSED_CAPTURES_DIR> $2 <PRELIM_OUTPUT_DIR>
	exit 1
fi

inputdir=$1
outputdir=$2

python make_pig_script_from_template.py initialized_religious_files None

pig -p ALL_PREPROCESSED_CAPTURES_DIR=$inputdir -p PRELIM_OUTPUT_DIR=$outputdir get_initialized_religious_files.pig
