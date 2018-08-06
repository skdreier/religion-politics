-- Author: Sofia Serrano
-- Get Keyword Counts TEMPLATE Pig Script: Template for automatically produced pig script which will count
-- the number of times each keyword provided in get_keyword_counts_keywords_to_count.txt occurs, as well as
-- reporting the words (that aren't already marked as non-matches) that that keyword appears in.
-- For questions contact sofias6@cs.washington.edu
-- This template script itself should never be run.
-- The automatically generated script can be run with only I_PARSED_DATA, O_DATA_DIR, and (if path to checksum
-- was originally provided as something other than None when script was automatically generated) I_CHECKSUM_DATA
-- arguments, assuming the output directory stub stub provided to the bash script that generated the script describes
-- directories that don't exist yet.
-- Example usage:
--     pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/ -p O_DATA_DIR=bucket2output \
--         -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ get_cooccurrence_words.pig
-- These first four lines are defaults and also help with memory (if you don't have them, sometimes the cluster kicks you out)

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER '../emilys_python_udfs.py' USING jython AS emilysfuncs;
REGISTER 'get_cooccurrence_words_udfs.py' USING jython AS cooccurrencefuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE converttochararray cooccurrencefuncs.converttochararray();
DEFINE append_placeholder cooccurrencefuncs.append_placeholder();

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- when you load data, you have to use the same "name" for the data that you do in the command line command -
-- so this is the name of the directory or file that you want to run this script on

Archive = LOAD '/user/lucylin/arcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/arcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/arcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/arcs/bucket-3/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance3 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/arcs/bucket-4/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance4 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/arcs/bucket-5/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance5 = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/warcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/warcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;

Archive = LOAD '/user/lucylin/warcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2w = FOREACH Archive GENERATE URL AS URLs,
                                     surt AS surt,
                                     checksum AS checksum,
                                     date AS date;


instance = UNION instance0, instance1, instance2, instance3, instance4, instance5, instance0w, instance1w, instance2w;

-- IF NOT BOTHERING WITH CHECKSUM: comment the next line out

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

-- IF NOT BOTHERING WITH CHECKSUM: comment the next line out

all_entries = JOIN instance BY (surt, checksum), Checksum BY (surt, checksum);

-- IF NOT BOTHERING WITH CHECKSUM: comment the next line out

all_entries = FOREACH all_entries GENERATE Checksum::date AS date,
                                           instance::URLs AS URL,
                                           instance::surt AS surt,
                                           instance::checksum AS checksum;

ordered_by_date = ORDER all_entries BY date ASC;

STORE ordered_by_date INTO 'all_dates/' USING PigStorage('\t');