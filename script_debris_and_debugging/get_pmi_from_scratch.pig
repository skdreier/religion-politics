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

all_cooccurring_words = FOREACH instance GENERATE FLATTEN(TOKENIZE(text, ' ')) AS word:chararray;

religious_cooccurring_wordcounts = FOREACH (GROUP all_cooccurring_words BY word) GENERATE FLATTEN(group) AS cooccurring_word:chararray,
                                                                                          COUNT(all_cooccurring_words) AS religious_wordcount:long;

corpus_counts = LOAD '/user/sofias6/lowercaseword_corpuscounts' USING PigStorage('\t') AS (term:chararray,
                                                                                  wordcount:long);

religious_cooccurring_wordcounts = JOIN religious_cooccurring_wordcounts BY cooccurring_word LEFT OUTER, corpus_counts BY term;

religious_cooccurring_wordcounts = FOREACH religious_cooccurring_wordcounts GENERATE religious_cooccurring_wordcounts::cooccurring_word AS word:chararray,
                                                                                     religious_cooccurring_wordcounts::religious_wordcount AS religious_wordcount:long,
                                                                                     (corpus_counts::wordcount == 0 ? 1 : corpus_counts::wordcount + 1) AS corpus_wordcount:long;

religious_cooccurring_wordcounts_with_prelim_pmi = FOREACH religious_cooccurring_wordcounts GENERATE word AS word,
                                                                                                     religious_wordcount AS religious_wordcount,
                                                                                                     corpus_wordcount AS corpus_wordcount,
                                                                                                     ((float) (religious_wordcount / 100000) / (float) ((corpus_wordcount + 10000000) / 100000)) AS pmi:float;

religious_cooccurring_wordcounts_with_prelim_pmi = ORDER religious_cooccurring_wordcounts_with_prelim_pmi BY pmi DESC;

STORE religious_cooccurring_wordcounts_with_prelim_pmi INTO 'prelim_pmi_alltime/' USING PigStorage('\t');
