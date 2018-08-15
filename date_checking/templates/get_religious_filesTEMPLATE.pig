SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER 'get_religious_files_udfs.py' USING jython AS paddingfuncs;

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();
DEFINE pad_str paddingfuncs.pad_string();

-- if loading from a directory where a space hasn't already been added to either end of the document,
-- then call pad_str on document to add those

instance = LOAD '/user/sofias6/all_religious_captures2/' USING PigStorage('\t') AS (URL:chararray,
                                                                                    surt:chararray,
                                                                                    checksum:chararray,
                                                                                    date:chararray,
                                                                                    code:chararray,
                                                                                    title:chararray,
                                                                                    description:chararray,
                                                                                    document:chararray);

religious_instance = FILTER instance BY
                                     STARTLINEREPEATATMOST25
                                     document MATCHES INSERTPIGREGEXHERE
                                     ENDLINEREPEATATMOST25

religious_instance = ORDER religious_instance BY date;

STORE religious_instance INTO 'all_religious_captures_filtered/' USING PigStorage('\t');

non_religious_instance = FILTER instance BY NOT(
                                     STARTLINEREPEATATMOST25
                                     document MATCHES INSERTPIGREGEXHERE
                                     ENDLINEREPEATATMOST25
                                     );

non_religious_instance = ORDER non_religious_instance BY date;

STORE non_religious_instance INTO 'rejected_religious_captures_for_qa_purposes/' USING PigStorage('\t');

religious_instance_no_text = FOREACH religious_instance GENERATE URLs AS URL,
                                                                 surt AS surt,
                                                                 checksum AS checksum,
                                                                 date AS date;

count_religious_instance_pre_checksum = GROUP religious_instance_no_text ALL;

counted_religious_instance_pre_checksum = FOREACH count_religious_instance_pre_checksum GENERATE COUNT(religious_instance_no_text) AS counted;

DUMP counted_religious_instance_pre_checksum;

Checksum = LOAD '/dataset/gov/url-ts-checksum/' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

all_entries = JOIN religious_instance_no_text BY (surt, checksum), Checksum BY (surt, checksum);

all_entries = FOREACH all_entries GENERATE Checksum::date AS date,
                                           religious_instance_no_text::URL AS URL,
                                           religious_instance_no_text::surt AS surt,
                                           religious_instance_no_text::checksum AS checksum;

ordered_by_date = ORDER all_entries BY date ASC;

STORE ordered_by_date INTO 'all_dates_religious_only_filtered/' USING PigStorage('\t');

for_counting = GROUP all_entries ALL;

for_counting = FOREACH for_counting GENERATE COUNT(all_entries) AS counted;

DUMP for_counting;