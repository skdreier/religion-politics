-- To run:
-- pig -p PATH_TO_URL_FILE=/a/sample/path/ -p ALL_PREPROCESSED_CAPTURES_DIR=/another/path/ \
--     -p CAPTURES_SUBSET_OUTPUT_DIR=a_sample_output_dir/ get_capture_subset_by_url.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

-- note to self: provided this arg as /user/lucylin/matches_2018-08-29.tsv

-- IF URL_FILE IS NOT IN THIS FORMAT, FEEL FREE TO CHANGE THIS LINE; just needs to have at least
-- surt and checksum fields in order for rest of script to work.

surts_checksums_to_pull = LOAD '$PATH_TO_URL_FILE' USING PigStorage('\t') AS (surt:chararray,
                                                                              checksum:chararray,
                                                                              date:chararray,
                                                                              text:chararray);

surts_checksums_to_pull = FOREACH surts_checksums_to_pull GENERATE surt AS surt:chararray,
                                                                   checksum AS checksum:chararray;

surts_checksums_to_pull = DISTINCT surts_checksums_to_pull;

-- note to self: since this was the directory I didn't make, this "argument" was actually provided
-- as the full /user/lucylin/(w)arcs/bucket-(0-5)/ and then a UNION

instance = LOAD '$ALL_PREPROCESSED_CAPTURES_DIR' USING PigStorage('\u0001') AS (URL:chararray,
                                                                                surt:chararray,
                                                                                checksum:chararray,
                                                                                date:chararray,
                                                                                code:chararray,
                                                                                title:chararray,
                                                                                description:chararray,
                                                                                content:chararray);

policy_match_full_corpus = JOIN surts_checksums_to_pull BY (surt, checksum) LEFT OUTER, instance BY (surt, checksum);

policy_match_full_corpus = DISTINCT policy_match_full_corpus;

-- note to self: provided this arg as full_lowercased_policy_docs/

STORE policy_match_full_corpus INTO '$CAPTURES_SUBSET_OUTPUT_DIR' USING PigStorage('\t');

for_counting = GROUP policy_match_full_corpus ALL;

for_counting = FOREACH for_counting GENERATE COUNT(policy_match_full_corpus) AS counted;

DUMP for_counting;
