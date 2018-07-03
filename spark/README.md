# README

## Prerequisites

I forgot to write down exactly what I did (oops), but the install list is
something like:
* sbt
* scala
* spark

(and maybe hadoop, though that's useful anyways)


## Build

Hopefully `sbt similarity/assembly` (from this directory) should work;
the output jar should be in `similarity/target/scala_2.11`.


## Run (local)

First, download a `.arc.gz` or `.warc.gz` file from
`/dataset-derived/gov/parsed/...` on the cluster. Note: unlike the unparsed
files in `/dataset/gov/...`, these are not actually gzipped (nor are they
standard arc or warc files); they are instead Hadoop sequence files.

Sanity check (load dataset, print first valid entry):
```
spark-submit --class relpol.similarity.SentenceSimilarity \
  similarity/target/scala-2.11/sentencesimilarity.jar \
  sanity \
  ./DOTGOV-EXTRACTION-1995-FY2013-MIME-APPLICATION-WARCS-PART-00000-000000.warc.gz
```

Running tokenization, etc. (doesn't fully work yet): swap `run` for `sanity`
above.


## Run (on cluster)

Environment variables to update before running (so that we get spark 2.1+ and
not 1.6):
* `SPARK_HOME`: set to `/opt/spark-beta`
* `SPARK_CONF_DIR`: set to `/etc/spark-beta`

Otherwise: ???
