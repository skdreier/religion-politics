# Religion and Politics
## Lucy Lin, Sofia Serrano, Emily Gade, Sarah Dreier

## Running scripts

1. Copy the repository up to your personal workbench

2. Run the command `source add_dependencies_to_classpath.sh` (this will add the jar files in the lib directory to your classpath and pig_classpath)

3. From the top-level directory of the repository, run some variation on the command `pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/ -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ -p O_DATA_DIR=outputARC2/ ExtractCounts_keywords.pig`, providing the local path from this directory to your desired pig script, and making sure that your provided value for O_DATA_DIR is not already a preexisting directory in the hadoop file system at `hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/`. (If, for example, `hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/outputARC2` already existed when the example command was run, the script would quit out for reasons related to "output validation.")

