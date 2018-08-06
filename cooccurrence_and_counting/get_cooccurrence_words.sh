#!/usr/bin/env bash

if [ "$#" -ne 6 ]
then
	echo "Usage: $1 <window size around search term> $2 <# top results to collect> $3 <local prefix of output dir> $4 <I_PARSED_DATA if skip_pig is False; path to directory stubs if skip_pig is True> $5 <I_CHECKSUM_DATA> $6 <{True, False}: skip pig steps, resume with pre-gathered pig results>"
	exit 1
fi

source add_dependencies_to_classpath.sh  # just in case this hasn't been done yet

windowsize=$1
numresultstocollect=$2
outputdirprefix=$3
input_data=$4
skip_pig=$6
nonpig_idf_multiprocessing_level=3

if [[ $skip_pig != True ]] ;
then
    python make_pig_script_from_template.py cooccurrence_words $windowsize $numresultstocollect $outputdirprefix $5

    pig -p I_PARSED_DATA=$4 -p I_CHECKSUM_DATA=$5 get_cooccurrence_words.pig
fi

if [[ $skip_pig == True ]] ;
then
   nonempty_filenames=($(ls -d -1 ${input_data}-fulltext/*.* | awk '{print $NF}' | tr '\n' ' '))
else
   nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdirprefix}-fulltext/ | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
fi
num_filenames=${#nonempty_filenames[@]}

fulltext_ending=-fulltext
if [[ $skip_pig == True ]] ;
then
   for i in "${!nonempty_filenames[@]}"; do
     cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_from_matches.py $outputdirprefix $num_filenames $windowsize $i
   done
else
   for i in "${!nonempty_filenames[@]}"; do
     hdfs dfs -cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_from_matches.py $outputdirprefix $num_filenames $windowsize $i
   done
fi

# will produce a file called $outputdirprefex-cooccurrencecounts.csv
# will also populate get_keyword_doc_counts_keywords_to_counts.txt in a preliminary way
python get_cooccurrence_words_aggregate_summaries.py $num_filenames $outputdirprefix

scp get_keyword_doc_counts_keywords_to_count.txt get_keyword_doc_counts_keywords_to_count_2.txt

# will now calculate idf for each foundword, and will store those
# in $outputdirprefix-foundwordestimatedcorpuscount.csv
if [[ $skip_pig == True ]] ;
then
   nonempty_filenames=($(ls -d -1 ${input_data}-sampledocfrequencies/*.* | awk '{print $NF}' | tr '\n' ' '))
else
   nonempty_filenames=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdirprefix}-sampledocfrequencies/ | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
fi
num_filenames=${#nonempty_filenames[@]}
fulltext_ending=-fulltext
if [[ $skip_pig == True ]] ;
then
    if [[ $nonpig_idf_multiprocessing_level != 1 ]] ; then
      filename_index=0
      num_batches=$(( $num_filenames / $nonpig_idf_multiprocessing_level ))
      if [[ $(($num_batches * $nonpig_idf_multiprocessing_level)) != $((num_filenames)) ]] ;
      then
        num_batches=$(($num_batches + 1))
      fi
      for j in `seq 0 $((${num_batches} - 1))`; do
        extra_filenames=''
        space=" "
        for i in `seq 0 $((${nonpig_idf_multiprocessing_level} - 1))`; do
          if [[ $filename_index != $num_filenames ]] ; then
            extra_filenames=$extra_filenames${nonempty_filenames[$filename_index]}$space
            filename_index=$(($filename_index + 1))
          fi
        done
        python get_cooccurrence_words_aggregate_idf.py $(($j * $nonpig_idf_multiprocessing_level)) $num_filenames $outputdirprefix $numresultstocollect $extra_filenames
      done

      nonempty_filenames=($(ls -d -1 ${input_data}-aggregateddocfrequencies/*.* | awk '{print $NF}' | tr '\n' ' '))
      num_filenames=${#nonempty_filenames[@]}
    else
      agg_doc_freq=-aggregateddocfrequencies/
      DIRECTORY=$input_data$agg_doc_freq
      if [ ! -d "$DIRECTORY" ]; then
        for i in "${!nonempty_filenames[@]}"; do
          cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_aggregate_idf.py $i $num_filenames $outputdirprefix $numresultstocollect
        done
      fi
      nonempty_filenames=($(ls -d -1 ${outputdirprefix}-aggregateddocfrequencies/*.* | awk '{print $NF}' | tr '\n' ' '))
      num_filenames=${#nonempty_filenames[@]}
    fi
else
    agg_doc_freq=-aggregateddocfrequencies/
    DIRECTORY=$outputdirprefix$agg_doc_freq
    if [ ! -d "$DIRECTORY" ]; then
      for i in "${!nonempty_filenames[@]}"; do
        hdfs dfs -cat ${nonempty_filenames[$i]} | python get_cooccurrence_words_aggregate_idf.py $i $num_filenames $outputdirprefix $numresultstocollect
      done
    fi
    nonempty_filenames=($(ls -d -1 ${outputdirprefix}-aggregateddocfrequencies/*.* | awk '{print $NF}' | tr '\n' ' '))
    num_filenames=${#nonempty_filenames[@]}
fi

filename_index=0
num_batches=$(( $num_filenames / $nonpig_idf_multiprocessing_level ))
if [[ $(($num_batches * $nonpig_idf_multiprocessing_level)) != $((num_filenames)) ]] ;
then
  num_batches=$(($num_batches + 1))
fi
for j in `seq 0 $((${num_batches} - 1))`; do
  extra_filenames=''
  space=" "
  for i in `seq 0 $((${nonpig_idf_multiprocessing_level} - 1))`; do
    if [[ $filename_index != $num_filenames ]] ; then
      extra_filenames=$extra_filenames${nonempty_filenames[$filename_index]}$space
      filename_index=$(($filename_index + 1))
    fi
  done
  python get_cooccurrence_words_calculate_foundword_doc_frequency.py $(($j * $nonpig_idf_multiprocessing_level)) $num_filenames $outputdirprefix $numresultstocollect $extra_filenames
done

append_count=-foundwordestimatedcorpuscount
csv_ending=.csv
cooccurrence_ending=-cooccurrencecounts.csv
python get_cooccurrence_words_calculate_from_tfidf_files.py $outputdirprefix$append_count$csv_ending $outputdirprefix$cooccurrence_ending $outputdirprefix $numresultstocollect

directory_end=-temp/
rm -r $outputdirprefix$directory_end

echo "Script complete."
