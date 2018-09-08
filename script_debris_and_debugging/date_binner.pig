SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;
REGISTER 'date_padding_udfs.py' USING jython AS datefuncs;

DEFINE make_correct_length datefuncs.pad_to_correct_length();

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- when you load data, you have to use the same "name" for the data that you do in the command line command -
-- so this is the name of the directory or file that you want to run this script on

all_records = LOAD '/user/sofias6/religious_house_senate_nonchecksum_dates/' USING PigStorage('\t') AS (date:chararray,
                                                                         URL:chararray,
                                                                         surt:chararray,
                                                                         checksum:chararray);

all_records = FOREACH all_records GENERATE make_correct_length(date) AS date:chararray,
                                           URL AS URL:chararray,
                                           surt AS surt:chararray,
                                           checksum AS checksum:chararray;

all_records = FOREACH all_records GENERATE (int) date AS date:int,
                                           URL AS URL:chararray,
                                           surt AS surt:chararray,
                                           checksum AS checksum:chararray;

all_records = FOREACH all_records GENERATE (date / ((int) $BIN_WIDTH)) AS bin_id,
                                                                                                              date AS date,
                                                                                                              URL AS URL;

bin_count = FOREACH (GROUP all_records BY bin_id) GENERATE FLATTEN(group) AS bin_id,
                                                           COUNT(all_records) AS num_in_bin;

bin_count = ORDER bin_count BY bin_id;

STORE bin_count INTO '$BINSPLIT-religiousunchecksum/' USING PigStorage('\t');

all_records_distinct_urls = DISTINCT all_records;

bin_count = FOREACH (GROUP all_records_distinct_urls BY bin_id) GENERATE FLATTEN(group) AS bin_id,
                                                           COUNT(all_records_distinct_urls) AS num_in_bin;

bin_count = ORDER bin_count BY bin_id;

STORE bin_count INTO '$BINSPLIT-religiousunchecksum-distincturl/' USING PigStorage('\t');