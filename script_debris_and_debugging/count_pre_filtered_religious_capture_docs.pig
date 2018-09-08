SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

instance = LOAD '/user/sofias6/all_religious_captures2' USING PigStorage('\t') AS (URL:chararray,
                                                                                    surt:chararray,
                                                                                    checksum:chararray,
                                                                                    date:chararray,
                                                                                    code:chararray,
                                                                                    title:chararray,
                                                                                    description:chararray,
                                                                                    document:chararray);

for_counting = GROUP instance ALL;

for_counting = FOREACH for_counting GENERATE COUNT(instance) AS counted;

DUMP for_counting;