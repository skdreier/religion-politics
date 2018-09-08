-- To sample an (approximate) number of files from the directory other than 200,
-- change the 200 in the line defining sampled_docs to something else.

-- To run:
-- pig -p DIR_TO_SAMPLE_FROM=/your/dir/with_preprocessed_captures -p OUTPUT_SAMPLE_DIR=an_output_dir/ \
--     sample_preprocessed_captures_from_directory.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- note to self: this arg was provided as /user/sofias6/all_religious_captures2/

instance = LOAD '$DIR_TO_SAMPLE_FROM' USING PigStorage('\t') AS (URL:chararray,
                                                                                   surt:chararray,
                                                                                   checksum:chararray,
                                                                                   date:chararray,
                                                                                   code:chararray,
                                                                                   title:chararray,
                                                                                   description:chararray,
                                                                                   document:chararray);

grouped = GROUP instance ALL;

num_religious_captures = FOREACH grouped GENERATE COUNT_STAR(instance) AS num_rows;

sampled_docs = SAMPLE instance (double)200/num_religious_captures.num_rows;

STORE sampled_docs INTO '$OUTPUT_SAMPLE_DIR' USING PigStorage('\t');
