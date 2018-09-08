SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

instance = LOAD '/user/sofias6/all_religious_captures2/' USING PigStorage('\t') AS (URL:chararray,
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

STORE sampled_docs INTO 'sample_religious_captures/' USING PigStorage('\t');
