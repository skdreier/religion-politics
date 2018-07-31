#!/usr/bin/env bash

if [ "$#" -ne 1 ]
then
    echo "Usage: $1 <name given to ssh portal to cluster>"
    exit 1
fi

clustername=$1
outputdirlocalname=url-ts-checksum/

slashending=/
if [[ $outputdirlocalname != */ ]] ;
then
   outputdirlocalname=$outputdirlocalname$slashending
fi

mkdir $outputdirlocalname

nonempty_filenames=($(ssh $clustername "hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/dataset/gov/url-ts-checksum/" | grep -v ' 0 ' | awk '{print $NF}' | grep ^hdfs | tr '\n' ' '))
num_filenames=${#nonempty_filenames[@]}
declare -a just_filenames
for i in "${!nonempty_filenames[@]}"; do
  just_filenames[$i]=$(basename ${nonempty_filenames[$i]})
done

txt_ending=.txt
for i in "${!nonempty_filenames[@]}"; do
  one_more=$(($i + 1))
  echo "Downloading non-empty file "$one_more" of "$num_filenames
  ssh $clustername "hdfs dfs -cat ${nonempty_filenames[$i]} " > $outputdirlocalname${just_filenames[$i]}$txt_ending
done
