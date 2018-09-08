-- bins dates by month, counts how many captures fall into each calendar distinct year-month pair.

-- Should only be run after get_nonchecksum_dates.pig has already been run.

-- To run:
-- pig -p DIR_WITH_DATES=/path/to/get_nonchecksum_dates/output/ \
--     -p FULL_BINNEDDATE_OUTPUT_DIR=sample_output_dir/ \
--     -p DISTINCT_URL_BINNEDDATE_PAIR_OUTPUT_DIR=another_output_dir/ \
--     date_binner_by_string.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

-- note to self: provided this argument as /user/sofias6/religious_house_senate_nonchecksum_dates/

all_records = LOAD '$DIR_WITH_DATES' USING PigStorage('\t') AS (date:chararray,
                                                                URL:chararray,
                                                                surt:chararray,
                                                                checksum:chararray);

all_records = FOREACH all_records GENERATE SUBSTRING(date, 0, 6) AS bin_id:chararray,
                                           URL AS URL:chararray;

bin_count = FOREACH (GROUP all_records BY bin_id) GENERATE FLATTEN(group) AS bin_id,
                                                           COUNT(all_records) AS num_in_bin;

bin_count = ORDER bin_count BY bin_id;

-- note to self: provided this argument as month-religiousunchecksum/

STORE bin_count INTO '$FULL_BINNEDDATE_OUTPUT_DIR' USING PigStorage('\t');

all_records_distinct_urls = DISTINCT all_records;

bin_count = FOREACH (GROUP all_records_distinct_urls BY bin_id) GENERATE FLATTEN(group) AS bin_id,
                                                           COUNT(all_records_distinct_urls) AS num_in_bin;

bin_count = ORDER bin_count BY bin_id;

-- note to self: provided this argument as month-religiousunchecksum-distincturl/

STORE bin_count INTO '$DISTINCT_URL_BINNEDDATE_PAIR_OUTPUT_DIR' USING PigStorage('\t');
