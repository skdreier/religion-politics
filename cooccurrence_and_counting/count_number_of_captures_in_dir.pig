-- To run:
-- pig -p DIR_WITH_CAPTURES_TO_COUNT=/dir/with/captures/ count_number_of_captures_in_dir.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- note to self: provided this arg as /user/sofias6/full_lowercased_policy_docs OR
-- /user/sofias6/policy_religious_captures_docsnippets_nonoverlapping OR
-- /user/sofias6/full_lowercased_policy_docs2/ OR
-- /user/sofias6/all_religious_captures2

instance2 = LOAD '$DIR_WITH_CAPTURES_TO_COUNT' USING PigStorage('\t') AS (URL:chararray,
                                                                          surt:chararray,
                                                                          checksum:chararray,
                                                                          date:chararray,
                                                                          code:chararray,
                                                                          title:chararray,
                                                                          description:chararray,
                                                                          content:chararray);

for_counting = GROUP instance2 ALL;

for_counting = FOREACH for_counting GENERATE COUNT(instance2) AS counted;

DUMP for_counting;
