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
REGISTER lib/porky-abbreviated.jar;
REGISTER lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER 'emilys_python_udfs.py' USING jython AS emilysfuncs;
REGISTER 'get_keyword_counts_udfs.py' USING jython AS keywordfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE converttochararray keywordfuncs.converttochararray();

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- when you load data, you have to use the same "name" for the data that you do in the command line command -
-- so this is the name of the directory or file that you want to run this script on

Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

-- generating the m# fields helps process the crazy .gz format into fields you can recognize (e.g. title; content)

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

-- this drops any files that return an error message

Archive = FILTER Archive BY m#'errorMessage' is null;

-- this is saying for each value and key pair, pull out the following fields.

instance = FOREACH Archive GENERATE emilysfuncs.pickURLs(m#'url'),                 -- adds URLs:chararray
              m#'url' AS src:chararray,                                            -- adds src:chararray
              SURTURL(m#'url') AS surt:chararray,                                  -- adds surt:chararray
              REPLACE(m#'digest','sha1:','') AS checksum:chararray,                -- adds checksum:chararray

              -- I kept getting unicode errors in the below fields, so I found a regular expression that means
              -- "all printed characters" e.g. NOT new lines, carriage returns, etc. SO. this finds anything
              -- that is not text, punctuation and white space, and replaces it with a space

              REPLACE(m#'code', '[^\\p{Graph}]', ' ')                               AS code:chararray,
              REPLACE(m#'title', '[^\\p{Graph}]', ' ')                              AS title:chararray,
              REPLACE(m#'description', '[^\\p{Graph}]', ' ')                        AS description:chararray,
              converttochararray(REPLACE(m#'content', '[^\\p{Alnum}\']', ' '))      AS document:chararray,

              -- This selects the first eight characters of the date string (year, month, day) -- I did this because
              -- the (year, month, day, hour, second) format is confusing for a lot of time formats down the line -
              -- python, postgresql, etc.

              REPLACE(SUBSTRING(m#'date', 0, 8), '[^\\p{Graph}]', ' ')              AS date:chararray;

-- don't bother looking through tokenized text for pages containing no matches
instance = FILTER instance BY NOT(document MATCHES '') AND (
                     STARTLINEREPEATATMOST25
                     document MATCHES INSERTPIGREGEXHERE
                     ENDLINEREPEATATMOST25
                     );

STORE instance INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-fulltext/' USING PigStorage('\u0001');
