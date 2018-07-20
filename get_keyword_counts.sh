#!/usr/bin/env bash

if [ "$#" -ne 3 ]
then
	echo "Usage: $1 <local prefix of output dir> $2 <I_PARSED_DATA> $3 <I_CHECKSUM_DATA>"
	exit 1
fi

source add_dependencies_to_classpath.sh  # just in case this has not been done yet

outputdir=$1
inputdir=$2
checksum=$3

python make_pig_script_from_template.py keyword_counts $checksum

pig -p I_PARSED_DATA=$inputdir -p O_DATA_DIR=$outputdir -p I_CHECKSUM_DATA=$checksum get_keyword_counts.pig

nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdir}/ | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
num_filenames=${#nonempty_filenames[@]}

for filename in "${nonempty_filenames[@]}"
do
    hdfs dfs -cat $filename | python get_keyword_counts_aggregate.py $outputdir $num_filenames;
done