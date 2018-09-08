SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

REGISTER 'lowercase_udf.py' USING jython AS lowercase;
DEFINE fix_format lowercase.lowercase_and_add_space_bookends();

-- This is how you would call out a to a python script with a designated function if you wanted to.

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

instance0 = LOAD '/user/lucylin/arcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1 = LOAD '/user/lucylin/arcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2 = LOAD '/user/lucylin/arcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance3 = LOAD '/user/lucylin/arcs/bucket-3/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance4 = LOAD '/user/lucylin/arcs/bucket-4/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance5 = LOAD '/user/lucylin/arcs/bucket-5/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0w = LOAD '/user/lucylin/warcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1w = LOAD '/user/lucylin/warcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2w = LOAD '/user/lucylin/warcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance = UNION instance0, instance1, instance2, instance3, instance4, instance5, instance0w, instance1w, instance2w;

instance = FOREACH instance GENERATE URL AS URL:chararray,
                                     surt AS surt:chararray,
                                     checksum AS checksum:chararray,
                                     date AS date:chararray,
                                     code AS code:chararray,
                                     title AS title:chararray,
                                     description AS description:chararray,
                                     fix_format(content) AS content:chararray;

all_words = FOREACH instance GENERATE FLATTEN(TOKENIZE(content, ' ')) AS word:chararray,
                                      date AS date:chararray;

corpus_wordcounts = FOREACH (GROUP all_words BY word) GENERATE FLATTEN(group) AS word_in_corpus:chararray,
                                                               COUNT(all_words) - 1 AS corpus_count_minus_1:long;

corpus_wordcounts = FILTER corpus_wordcounts BY corpus_count_minus_1 > 0;

STORE corpus_wordcounts INTO 'lowercaseword_corpuscounts/' USING PigStorage('\t');
