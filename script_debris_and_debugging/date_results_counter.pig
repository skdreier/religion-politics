SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- when you load data, you have to use the same "name" for the data that you do in the command line command -
-- so this is the name of the directory or file that you want to run this script on

all_records = LOAD '/user/sofias6/all_dates/' USING PigStorage('\t') AS (date:chararray,
                                                                         URL:chararray,
                                                                         surt:chararray,
                                                                         checksum:chararray);

unique_surts_checksums = FOREACH (GROUP all_records BY checksum) GENERATE FLATTEN(group) AS checksum;

unique_surts_checksums = ORDER unique_surts_checksums BY checksum;

--grouped = GROUP unique_surts_checksums ALL;

--number_records = FOREACH grouped GENERATE COUNT(unique_surts_checksums);

--DUMP number_records;

STORE unique_surts_checksums INTO 'checksums/' USING PigStorage('\t');



unique_surts_checksums = FOREACH (GROUP all_records BY (checksum, surt)) GENERATE FLATTEN(group) AS (checksum, surt);

unique_surts_checksums = ORDER unique_surts_checksums BY checksum;

--grouped = GROUP unique_surts_checksums ALL;

--number_records = FOREACH grouped GENERATE COUNT(unique_surts_checksums);

--DUMP number_records;

STORE unique_surts_checksums INTO 'surts_checksums/' USING PigStorage('\t');



unique_surts_checksums = FOREACH (GROUP all_records BY (URL, surt, checksum)) GENERATE FLATTEN(group) AS (URL, surt, checksum);

unique_surts_checksums = ORDER unique_surts_checksums BY URL;

--grouped = GROUP unique_surts_checksums ALL;

--number_records = FOREACH grouped GENERATE COUNT(unique_surts_checksums);

--DUMP number_records;

STORE unique_surts_checksums INTO 'urls_surts_checksums/' USING PigStorage('\t');



unique_surts_checksums = FOREACH (GROUP all_records BY URL) GENERATE FLATTEN(group) AS URL;

unique_surts_checksums = ORDER unique_surts_checksums BY URL;

--grouped = GROUP unique_surts_checksums ALL;

--number_records = FOREACH grouped GENERATE COUNT(unique_surts_checksums);

--DUMP number_records;

STORE unique_surts_checksums INTO 'urls/' USING PigStorage('\t');