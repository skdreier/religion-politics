#!/usr/bin/env bash

if [ "$#" -ne 1 ]
then
	echo "Usage: $1 <local prefix of directory in hdfs file system>"
	exit 1
fi

outputdir=$1

nonempty_filesizes=($(hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/$(whoami)/${outputdir}/ | sed -n "s/^.*users\s*\(\S*\).*$/\1/p" | tr '\n' ' '))

total=0
for i in ${nonempty_filesizes[@]}; do
  let total+=$i
done
echo "Total size of all files: $total"