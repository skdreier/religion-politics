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

-- all_religious_captures2

instance = LOAD '/user/sofias6/all_religious_captures2' USING PigStorage('\t') AS (URL:chararray,
                                                                                    surt:chararray,
                                                                                    checksum:chararray,
                                                                                    date:chararray,
                                                                                    code:chararray,
                                                                                    title:chararray,
                                                                                    description:chararray,
                                                                                    document:chararray);

all_religious_dates = LOAD '/user/sofias6/all_dates_religious_only_filtered' USING PigStorage('\t') AS (date:chararray,
                                                                                                        URL:chararray,
                                                                                                        surt:chararray,
                                                                                                        checksum:chararray);

all_religious_docs_duplicated = JOIN instance BY (surt, checksum, URL), all_religious_dates BY (surt, checksum, URL);

all_religious_docs_duplicated = FOREACH all_religious_docs_duplicated GENERATE instance::URL AS URL,
                                                                               instance::surt AS surt,
                                                                               instance::checksum AS checksum,
                                                                               instance::date AS date,
                                                                               instance::code AS code,
                                                                               instance::title AS title,
                                                                               instance::description AS description,
                                                                               instance::document AS document;

all_religious_docs = DISTINCT all_religious_docs_duplicated;

STORE all_religious_docs INTO 'all_religious_captures_filtered_2ndtime/' USING PigStorage('\t');

for_counting = GROUP all_religious_docs ALL;

for_counting = FOREACH for_counting GENERATE COUNT(all_religious_docs) AS counted;

DUMP for_counting;