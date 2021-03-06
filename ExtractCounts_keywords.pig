-- Author: Emily Kalah Gade
-- Threats Pig Script: Flags all captures whose content includes at least one mention of threat related terms
-- and also one mention of a crisis related term and stores the output
-- For questions contact ekgade@uw.edu
-- TO RUN: type something like this into the command line after having logged in the altiscale cluster with your ssh key:
--     pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-4/ -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ \
--         -p O_DATA_DIR=outputARC4/ -p O_DATA_DIR_2=outputARC4-2/ ExtractCounts_keywords.pig
-- make sure that your file paths are in the right place and that you start in the right directory (it doesn't give
-- you clear errors about this) If you want to run on a single arc or warc file, just add the filename after
-- bucket-4/ in the I_PARSED_DATA filepath

-- These first four lines are defaults and also help with memory (if you don't have them, sometimes the cluster kicks you out)

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/porky-abbreviated.jar;
REGISTER lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.
-- I used this for RegEx matching but it's much slower so I switched to the long "or" statement you see below.
-- However, if you are more comfortable with user defined functions in Python then this is what you do

REGISTER 'emilys_python_udfs.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();

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
-- the myfuncs. lines call the python functions from emilys_python_udfs.py, also in this repository

ExtractedCounts = FOREACH Archive GENERATE myfuncs.pickURLs(m#'url'),              -- adds URLs:chararray
           m#'url' AS src:chararray,                                               -- adds src:chararray
           myfuncs.Threat_countWords(REPLACE(m#'content', '[^\\p{Graph}]', ' ')),  -- adds counts:bag{tuple(word:chararray,count:int)}
           SURTURL(m#'url') AS surt:chararray,                                     -- adds surt:chararray
           REPLACE(m#'digest','sha1:','') AS checksum:chararray,                   -- adds checksum:chararray

           -- I kept getting unicode errors in the below fields, so I found a regular expression that means "all printed characters"
           -- e.g. NOT new lines, carriage returns, etc. SO. this finds anything that is not text, punctuation and white space,
           -- and replaces it with a space

           REPLACE(m#'code', '[^\\p{Graph}]', ' ')                               AS code:chararray,
           REPLACE(m#'title', '[^\\p{Graph}]', ' ')                              AS title:chararray,
           REPLACE(m#'description', '[^\\p{Graph}]', ' ')                        AS description:chararray,
           REPLACE(m#'content', '[^\\p{Graph}]', ' ')                            AS content:chararray,

           -- This selects the first eight characters of the date string (year, month, day) -- I did this because the
           -- (year, month, day, hour, second) format is confusing for a lot of time formats down the line - python, postgresql, etc.

           REPLACE(SUBSTRING(m#'date', 0, 8), '[^\\p{Graph}]', ' ')              AS date:chararray;

-- This takes each of the previous fields (the url, date, content, etc.) and searches
-- through the content field looking for any RegEx matches to these terms
-- If it finds one, it keeps it; otherwise "filter" drops the file

UniqueCaptures = FILTER ExtractedCounts BY content MATCHES '.*natural\\s+disaster.*'
                                        OR content MATCHES '.*desertification.*'
                                        OR content MATCHES '.*climate\\s+change.*'
                                        OR content MATCHES '.*pollution.*'
                                        OR content MATCHES '.*ocean\\s+acidification.*'
                                        OR content MATCHES '.*anthropocene.*'
                                        OR content MATCHES '.*anthropogenic.*'
                                        OR content MATCHES '.*greenhouse\\s+gas.*'
                                        OR content MATCHES '.*climategate.*'
                                        OR content MATCHES '.*climatic\\s+research\\s+unit.*'
                                        OR content MATCHES '.*security\\s+of\\s+food.*'
                                        OR content MATCHES '.*global\\s+warming.*'
                                        OR content MATCHES '.*fresh\\s+water.*'
                                        OR content MATCHES '.*forest\\s+conservation.*'
                                        OR content MATCHES '.*food\\s+security.*'
                                        OR content MATCHES '.*wmd..*'
                                        OR content MATCHES  '.*weapon[a-z]+?\\sof\\smass\\s+destruction.*'
                                        OR content MATCHES  '.*violat[a-z]+?\\s?o?f?\\su?n?i?v?e?r?s?a?l?\\s?human\\sright.*'
                                        OR content MATCHES '.*transnational\\s+crim.*'
                                        OR content MATCHES '.*terrorist.*'
                                        OR content MATCHES '.*terrorism.*'
                                        OR content MATCHES '.*taliban.*'
                                        OR content MATCHES '.*proliferat.*'
                                        OR content MATCHES '.*iran.*'
                                        OR content MATCHES '.*north\\s+korea.*'
                                        OR content MATCHES '.*natural\\s+disaster.*'
                                        OR content MATCHES '.*money\\s+launder.*'
                                        OR content MATCHES '.*ksts.*'
                                        OR content MATCHES '.*known\\s+and\\s+suspected\\s+terror.*'
                                        OR content MATCHES '.*organized\\s+crime.*'
                                        OR content MATCHES '.*human\\s+rights\\s+violat.*'
                                        OR content MATCHES '.*human\\s+rights\\s+abuse.*'
                                        OR content MATCHES '.*fresh\\s+water.*'
                                        OR content MATCHES '.*fragile\\s+state.*'
                                        OR content MATCHES '.*failed\\s+state.*'
                                        OR content MATCHES '.*state\\s+failure.*'
                                        OR content MATCHES '.*drug\\s+traffic.*'
                                        OR content MATCHES '.*disease.*'
                                        OR content MATCHES '.*pandemic.*'
                                        OR content MATCHES '.*cyberwar.*'
                                        OR content MATCHES '.*cyberterror.*'
                                        OR content MATCHES '.*cybersecurit.*'
                                        OR content MATCHES '.*cyber\\s+attack.*'
                                        OR content MATCHES '.*criminal\\s+network.*'
                                        OR content MATCHES '.*criminal\\s+baron.*'
                                        OR content MATCHES '.*chemical\\?\\sbiological\\?\\so?r?\\s?a?n?d?\\s?nuclear\\s?w?e?a?p?o?n?.*'
                                        OR content MATCHES '.*nuclear\\s+weapon.*'
                                        OR content MATCHES '.*chemical\\s+weapon.*'
                                        OR content MATCHES '.*bioterror.*'
                                        OR content MATCHES '.*biological\\s+weapon.*'
                                        OR content MATCHES '.*securities.*'
                                        OR content MATCHES'.*housing\\s+crisis.*'
                                        OR content MATCHES '.*subprime\\s+mortgage.*'
                                        OR content MATCHES '.*lending\\s+crisis.*'
                                        OR content MATCHES '.*market.*'
                                        OR content MATCHES '.*mortgage.*'
                                        OR content MATCHES '.*loan.*'
                                        OR content MATCHES '.*bankrupt.*'
                                        OR content MATCHES '.*toxic\\s+asset.*'
                                        OR content MATCHES '.*securities.*';

-- If you then wanted to further filter those terms by another set of terms, for example, you wanted a page
-- that mentioned global warming but also talked about it as a "threat" or a "crisis"... You could run this bit:

UniqueCaptures = FILTER UniqueCaptures BY content MATCHES '.*threat.*'
                                       OR content MATCHES '.*crisis.*'
                                       OR content MATCHES '.*security.*'
                                       OR content MATCHES '.*calamity.*'
                                       OR content MATCHES '.*catastroph.*'
                                       OR content MATCHES '.*disaster.*';

-- to get TOTAL number of counts, rather than simply unique observations, merge with checksum data.
-- (A unique capture will only have been taken if something changed on the page, but if one page changed
-- many times over a period of time and another stayed the same during that time, taking only the unique
-- captures into account will cause data from pages with consistent text to be underrepresented in our
-- analysis. The checksum data stores instances when a page *would* have been captured, but nothing had
-- changed; merging with the checksum data fixes the consistent page underrepresentation problem.)

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

-- this joins the unique counts with duplicate counts

CountsJoinChecksum = JOIN UniqueCaptures BY (surt, checksum), Checksum BY (surt, checksum);

-- this generates a set of full counts (so it duplicates the counts from the unique obs for the duplicate obs)
-- I only kept the fields I was interested in - because I'm planning to aggregate across URL group, I dropped the content field

FullCounts = FOREACH CountsJoinChecksum GENERATE
                            UniqueCaptures::src as src,
                            Checksum::date as date,
                            UniqueCaptures::counts as counts,
                            UniqueCaptures::URLs as URLs;

-- This would sort counts by original "source" or URL

GroupedCounts = GROUP FullCounts BY URLs;

-- This fills in the missing counts (it assumes the counts are the same for time in-between two captures,
-- rather than that the page disappeared. If the page did disappear (no last capture) this stops replicating it)

GroupedCounts = FOREACH GroupedCounts GENERATE
      group AS src,
      FLATTEN(myfuncs.fillInCounts(FullCounts)) AS (year:int, month:int, word:chararray, count:int, filled:int,
                                                    afterlast:int, URLs:chararray);

GroupedCounts2 = FOREACH GroupedCounts GENERATE
      year AS year, month AS month, word AS word, count AS count, afterlast AS afterlast, URLs AS URLs;

-- This stores the counts in the file name you gave it

STORE GroupedCounts2 INTO '$O_DATA_DIR';

-- The "using pigstorage" function allows you to set your own delimiters.
-- I chose one with Unicode because I was worried commas/tabs would show up in the existing text (obviously).
-- And, since I stripped out all unicode above, this should be clearly a new field

STORE UniqueCaptures INTO '$O_DATA_DIR_2' USING PigStorage('\u0001');
