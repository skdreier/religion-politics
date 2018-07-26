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

python make_pig_script_from_template.py cooccurrence_words $windowsize $numresultstocollect $outputdirprefix $5

pig -p I_PARSED_DATA=$4 -p I_CHECKSUM_DATA=$5 get_cooccurrence_words.pig

nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdirprefix}-fulltext/ | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
num_filenames=${#nonempty_filenames[@]}

fulltext_ending=-fulltext
for i in "${!nonempty_filenames[@]}"; do
  hdfs dfs -cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_from_matches.py $outputdirprefix $num_filenames $windowsize $i
done

# will produce a file called $outputdirprefex-cooccurrencecounts.csv
# will also populate get_keyword_doc_counts_keywords_to_counts.txt
python get_cooccurrence_words_aggregate_summaries.py $num_filenames $outputdirprefix

append_count=-foundwordcorpuscount
# this will produce a text file called $outputdirprefix-foundwordcorpuscount.csv containing the count of the number
# documents that each word in get_keyword_doc_counts_keywords_to_counts.txt appears in
bash get_keyword_doc_counts.sh $outputdirprefix$append_count $4 $5

csv_ending=.csv
cooccurrence_ending=-cooccurrencecounts.csv
python get_cooccurrence_words_calculate_from_tfidf_files.py $outputdirprefix$append_count$csv_ending $outputdirprefix$cooccurrence_ending $outputdirprefix $numresultstocollect

directory_end=-temp/
rm -r $outputdirprefix$directory_end