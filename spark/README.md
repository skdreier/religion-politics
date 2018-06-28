# README

## Prerequisites

I forgot to write down exactly what I did (oops), but the install list is
something like:
* sbt
* scala
* spark

(and maybe hadoop, though that's useful anyways)


## Build

Hopefully `sbt package` (from this directory) should work; the output jar
should be in `target/scala_2.11'.


## Run (local)

First, download a `.arc.gz` or `.warc.gz` file from
`/dataset-derived/gov/parsed/...` on the cluster. Note: unlike the unparsed
files in `/dataset/gov/...`, these are not actually gzipped (nor are they
standard arc or warc files); they are instead Hadoop sequence files.

Sanity check (load dataset, print first valid entry):
```
spark-submit --class SentenceSimilarity \
  target/scala-2.11/sentencesimilarity_2.11-0.1.jar \
  sanity \
  ./DOTGOV-EXTRACTION-1995-FY2013-MIME-APPLICATION-WARCS-PART-00000-000000.warc.gz
```

Running tokenization, etc. (doesn't fully work yet): swap `run` for `sanity`
above.


## Run (on cluster)

???
