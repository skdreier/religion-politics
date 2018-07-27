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
# will also populate get_keyword_doc_counts_keywords_to_counts.txt in a preliminary way
python get_cooccurrence_words_aggregate_summaries.py $num_filenames $outputdirprefix

# will now estimate idf for each foundword based on ~5000 or so randomly sampled documents from the given
# data source, and will store those in $outputdirprefix-foundwordcorpuscount.csv
nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdirprefix}-sampledocfrequencies/ | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
num_filenames=${#nonempty_filenames[@]}
fulltext_ending=-fulltext
for i in "${!nonempty_filenames[@]}"; do
  hdfs dfs -cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_estimate_foundword_doc_frequency.py $i $num_filenames $outputdirprefix $numresultstocollect
done

append_count=-foundwordestimatedcorpuscount
csv_ending=.csv
cooccurrence_ending=-cooccurrencecounts.csv
python get_cooccurrence_words_calculate_from_tfidf_files.py $outputdirprefix$append_count$csv_ending $outputdirprefix$cooccurrence_ending $outputdirprefix $numresultstocollect

directory_end=-temp/
rm -r $outputdirprefix$directory_end