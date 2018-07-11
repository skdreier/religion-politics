-- Author: Sofia Serrano
-- Get Cooccurrence Words TEMPLATE Pig Script: Template for automatically produced pig script which will find
-- notable words (i.e., not words like "and" or "the") that tend to cooccur with the words provided in
-- cooccurrence_search_words.txt.
-- For questions contact sofias6@cs.washington.edu
-- This template script itself should never be run.
-- The automatically generated script can be run without only I_PARSED_DATA and I_CHECKSUM_DATA argument,
-- assuming the output directory stub stub provided to the bash script that generated the script describes
-- directories that don't exist yet.
-- Example usage:
--     pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/ \
--         -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ get_cooccurrence_words.pig

-- These first four lines are defaults and also help with memory
-- (if you don't have them, sometimes the cluster kicks you out)

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/porky-abbreviated.jar;
REGISTER lib/webarchive-commons-1.1.7.jar;

REGISTER 'emilys_python_udfs.py' USING jython AS emilysfuncs;
REGISTER 'cooccurrence_udfs.py' USING jython AS cooccurrencefuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE docmakingudf cooccurrencefuncs.docmakingudf();
DEFINE converttochararray cooccurrencefuncs.converttochararray();

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
              REPLACE(m#'content', '[^\\p{Graph}]', ' ')                            AS document:chararray,

              -- This selects the first eight characters of the date string (year, month, day) -- I did this because
              -- the (year, month, day, hour, second) format is confusing for a lot of time formats down the line -
              -- python, postgresql, etc.

              REPLACE(SUBSTRING(m#'date', 0, 8), '[^\\p{Graph}]', ' ')              AS date:chararray;

prechecksum_instance = FOREACH instance GENERATE URLs AS URLs:chararray,
                                                 src AS src:chararray,
                                                 surt AS surt:chararray,
                                                 checksum AS checksum:chararray,
                                                 code AS code:chararray,
                                                 title AS title:chararray,
                                                 description AS description:chararray,
                                                 converttochararray(document) AS document:chararray,
                                                 date AS date:chararray;

-- to get TOTAL number of counts, rather than simply unique observations, merge with checksum data.
-- (A unique capture will only have been taken if something changed on the page, but if one page changed
-- many times over a period of time and another stayed the same during that time, taking only the unique
-- captures into account will cause data from pages with consistent text to be underrepresented in our
-- analysis. The checksum data stores instances when a page *would* have been captured, but nothing had
-- changed; merging with the checksum data fixes the consistent page underrepresentation problem.)

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

term_specific_doc_snippet = FOREACH prechecksum_instance GENERATE
                               STARTLINEREPEAT
							   FLATTEN(docmakingudf(document, INSERTTERMHERE, INSERTREGEXHERE, INSERTWINDOWSIZEHERE)),
							   surt AS surt:chararray,
                               checksum AS checksum:chararray
							   ENDLINEREPEAT

        -- format of term_specific_doc_snippet: ('pray', 'doc snippet with term edited out', surt, checksum)
		--                                      ('pray', 'and another fake document snippet', surt, checksum)
        --                                      ('crusade', 'suppose this term only had one match', surt, checksum)

searchterm_foundterm = FOREACH term_specific_doc_snippet GENERATE
                               term_specific_doc_snippet.searchterm AS search_term,
                               FLATTEN(TOKENIZE(term_specific_doc_snippet.text)),
                               surt AS surt:chararray,
                               checksum AS checksum:chararray;

        -- format of searchterm_foundterm: ('pray', 'doc', surt, checksum)
        --                                 ('pray', 'snippet', surt, checksum)
        --                                 ('pray', 'with', surt, checksum)
        --                                 ...
        --                                 ('crusade', 'suppose', surt, checksum)
        --                                 ...

-- IF NOT BOTHERING WITH CHECKSUM: just comment the next line out

searchterm_foundterm = JOIN searchterm_foundterm BY (surt, checksum), Checksum BY (surt, checksum);

searchterm_foundterm_count = FOREACH (GROUP searchterm_foundterm BY (search_term, $1)) GENERATE
                                FLATTEN(group) AS (search_term, term),
                                COUNT(searchterm_foundterm) AS foundtermcount;

searchterm_foundterm_count = FOREACH (GROUP searchterm_foundterm_count by (search_term)) GENERATE
                                search_term AS search_term:chararray,
                                term AS term:chararray,
                                foundtermcount AS foundtermcount:int,
                                SUM(foundtermcount) AS numwordsinsearchtermdoc;

foundterm_count_all_searchwords = FOREACH(GROUP searchterm_foundterm BY $1) GENERATE
                                                group.$1 AS term,
                                                COUNT(searchterm_foundterm) AS foundtermcount;

-- Now compute word totals across the corpus that will be used as the IDF piece

Docs = FOREACH prechecksum_instance GENERATE document AS doc,
                                             surt AS surt:chararray,
                                             checksum AS checksum:chararray,
                                             date AS date:chararray,
                                             FLATTEN(TOKENIZE(document)) as term;

-- IF NOT BOTHERING WITH CHECKSUM: just comment the next line out

Docs = JOIN Docs BY (surt, checksum), Checksum BY (surt, checksum);

DocWordTotals = FOREACH (GROUP Docs by (doc, term)) GENERATE FLATTEN(group) as (doc, term), COUNT(Docs) as docTotal;

TermCounts = FOREACH (GROUP DocWordTotals by doc) GENERATE
                      group AS doc,
                      FLATTEN(DocWordTotals.(term, docTotal)) as (term, docTotal),
                      SUM(DocWordTotals.docTotal) as docSize;

-- get number of docs containing a given term
word_totals = FOREACH (GROUP TermCounts BY term) GENERATE term AS term,
                                                          SUM(docTotal) AS corpuscount;
                                                          COUNT(TermCounts) AS occursinnumdocs;

-- now add that new information to previously computed information to compute scores that will be used
-- to rank words in two separate ways

info_to_compute_term_scores = JOIN searchterm_foundterm_count BY term LEFT OUTER, word_totals BY term;

        -- format of output: ('pray', 'a', docpieceafreq, #aincorpus, #docswitha, numwordsinsearchtermdoc)
        --                   ('pray', 'fake', docpiecefakefreq, #fakeincorpus, #docswithfake, numwordsinsearchtermdoc)
        --                   ...

table_with_log_scores = FOREACH info_to_compute_term_scores {
                           log_idf_corpus = 0.0 - LOG((double) corpuscount);
                           log_idf_doc = 0.0 - LOG((double) occursinnumdocs);
                           log_tf_score = LOG((double) foundtermcount);
                           GENERATE search_term AS search_term,
                                    term AS term,
                                    log_tf_score + log_idf_corpus AS score_corpus,
                                    log_tf_score + log_idf_doc AS score_doc,
                                    LOG(numwordsinsearchtermdoc) AS lognumwordsinsearchtermdoc;
};

-- Sort, trim, and store results

-------------- Output by considering the highest (re-weighted) score of results for *any* search word --------------

subtable = FOREACH table_with_log_scores GENERATE search_term AS search_term,
                                                  term AS term,
                                                  score_corpus - lognumwordsinsearchtermdoc AS score_corpus,
                                                  score_doc - lognumwordsinsearchtermdoc AS score_doc;
order_by_score_corpus = ORDER subtable BY score_corpus DESC;
order_by_score_corpus = LIMIT order_by_score_corpus INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_corpus GENERATE search_term as search_term,
                                                          term as term,
                                                          score_corpus as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-anysearchword-corpus/';

order_by_score_doc = ORDER subtable BY score_doc DESC;
order_by_score_doc = LIMIT order_by_score_doc INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_doc GENERATE search_term as search_term,
                                                       term as term,
                                                       score_doc as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-anysearchword-doc/';

-------------- Output from collapsing all search words into one "keyword" --------------

info_to_compute_agg_term_scores = JOIN foundterm_count_all_searchwords BY term LEFT OUTER, word_totals BY term;

        -- format of output: ('a', docpieceafreq, #aincorpus, #docswitha, numwordsinsearchtermdoc)
        --                   ('fake', docpiecefakefreq, #fakeincorpus, #docswithfake, numwordsinsearchtermdoc)
        --                   ...


table_with_log_agg_scores = FOREACH info_to_compute_agg_term_scores {
                               log_idf_corpus = 0.0 - LOG((double) corpuscount);
                               log_idf_doc = 0.0 - LOG((double) occursinnumdocs);
                               log_tf_score = LOG((double) foundtermcount);
                               GENERATE search_term AS search_term,
                                        term AS term,
                                        log_tf_score + log_idf_corpus AS score_corpus,
                                        log_tf_score + log_idf_doc AS score_doc;
};

subtable = table_with_agg_log_scores;
order_by_score_corpus = ORDER subtable BY score_corpus DESC;
order_by_score_corpus = LIMIT order_by_score_corpus INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_corpus GENERATE term as term,
                                                          score_corpus as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-allsearchwords-corpus/';

order_by_score_doc = ORDER subtable BY score_doc DESC;
order_by_score_doc = LIMIT order_by_score_doc INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_doc GENERATE term as term,
                                                       score_doc as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-allsearchwords-doc/';

-------------- Output from each individual search word --------------

STARTLINEREPEAT
subtable = FILTER table_with_log_scores BY search_term == INSERTTERMHERE;
order_by_score_corpus = ORDER subtable BY score_corpus DESC;
order_by_score_corpus = LIMIT order_by_score_corpus INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_corpus GENERATE search_term as search_term,
                                                          term as term,
                                                          score_corpus as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES-corpus/';

order_by_score_doc = ORDER subtable BY score_doc DESC;
order_by_score_doc = LIMIT order_by_score_doc INSERTNUMTERMSTOCOLLECT;
subtable_to_dump = FOREACH order_by_score_doc GENERATE search_term as search_term,
                                                       term as term,
                                                       score_doc as score;
STORE subtable_to_dump INTO 'INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES-INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES-doc/';

ENDLINEREPEAT
