#!/usr/bin/env bash

# CAREFUL: this script is somewhat brittle due to UDF variable-return-type weirdness.
# Might need to switch to something more similar to the document frequency collecting
# setup in get_cooccurrence_words.sh.

if [ "$#" -ne 3 ]
then
	echo "Usage: $1 <local prefix of output dir> $2 <I_PARSED_DATA> $3 <I_CHECKSUM_DATA>"
	exit 1
fi

source add_dependencies_to_classpath.sh  # just in case this has not been done yet

outputdir=$1
inputdir=$2
checksum=$3

python make_pig_script_from_template.py keyword_doc_counts $checksum

pig -p I_PARSED_DATA=$inputdir -p O_DATA_DIR=$outputdir -p I_CHECKSUM_DATA=$checksum get_keyword_doc_counts.pig

nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdir}* | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
num_filenames=${#nonempty_filenames[@]}

for filename in "${nonempty_filenames[@]}"
do
    hdfs dfs -cat $filename | python get_keyword_doc_counts_aggregate.py $outputdir $num_filenames $filename;
done

echo "Script complete."
