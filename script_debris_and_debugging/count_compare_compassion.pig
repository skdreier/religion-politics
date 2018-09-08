SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER 'get_religious_snippets_udfs.py' USING jython AS paddingfuncs;

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();
DEFINE docmakingudf paddingfuncs.docmakingudf();


instance = LOAD '/user/sofias6/all_religious_captures_docsnippets_nonoverlapping' USING PigStorage('\t') AS (searchterm:chararray,
                                                                                    text:chararray,
                                                                                    URL:chararray,
                                                                                    surt:chararray,
                                                                                    checksum:chararray,
                                                                                    date:chararray,
                                                                                    code:chararray,
                                                                                    title:chararray,
                                                                                    description:chararray);

instance = FILTER instance BY text MATCHES '.*compassion.*';

all_cooccurring_words = FOREACH instance GENERATE FLATTEN(TOKENIZE(text, ' ')) AS word:chararray,
                                                                         surt AS surt,
                                                                         checksum AS checksum;

all_cooccurring_words = FILTER all_cooccurring_words BY word MATCHES 'compassion';

compassion_counts = FOREACH (GROUP all_cooccurring_words BY (surt, checksum)) GENERATE FLATTEN(group) AS (surt, checksum),
                                                                                       COUNT(all_cooccurring_words) AS compassion_count:long;

compassion_counts = ORDER compassion_counts BY compassion_count DESC;

STORE compassion_counts INTO 'religious_match_compassion_counts/' USING PigStorage('\t');

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

instance_full = UNION instance0, instance1, instance2, instance3, instance4, instance5, instance0w, instance1w, instance2w;

instance_full = FILTER instance_full BY content MATCHES '.*compassion.*';

all_cooccurring_words_full = FOREACH instance_full GENERATE FLATTEN(TOKENIZE(content, ' ')) AS word:chararray,
                                                                         surt AS surt,
                                                                         checksum AS checksum;

all_cooccurring_words_full = FILTER all_cooccurring_words_full BY word MATCHES 'compassion';

compassion_counts_full_corpus = FOREACH (GROUP all_cooccurring_words_full BY (surt, checksum)) GENERATE FLATTEN(group) AS (surt, checksum),
                                                                                       COUNT(all_cooccurring_words_full) AS compassion_count:long;

compassion_counts_full_corpus = ORDER compassion_counts_full_corpus BY compassion_count DESC;

STORE compassion_counts_full_corpus INTO 'full_corpus_compassion_counts/' USING PigStorage('\t');

joined = JOIN compassion_counts_full_corpus BY (surt, checksum) LEFT OUTER, compassion_counts BY (surt, checksum);

joined = FOREACH joined GENERATE compassion_counts_full_corpus::compassion_count AS full_corpus_compassion_count,
                                 compassion_counts::compassion_count AS religious_compassion_count,
                                 (compassion_counts_full_corpus::compassion_count - compassion_counts::compassion_count) AS diff_compassion:long,
                                 compassion_counts_full_corpus::surt AS surt,
                                 compassion_counts_full_corpus::checksum AS checksum;

joined = ORDER joined BY diff_compassion ASC;

STORE joined INTO 'compassion_comparison/' USING PigStorage('\t');



