-- Currently has an extra 10,000,000 fake counts added to each word's corpus frequency
-- during PMI calculation. To change, replace the 10,000,000 in line 94 with something else.

-- To run:

-- pig -p FILTERED_RELIGIOUS_CAPTURE_DIR=/dir/of/preprocessed/religious/captures/ \
--     -p RELIGIOUS_SNIPPETS_DIR=dir_to_save_extracted_religious_snippets_in/    \
--     -p ALL_PREPROCESSED_CAPTURES_DIR=/path/to/dir                              \
--     -p CORPUSWIDE_WORDCOUNTS=dir_to_save_calculated_corpuswide_wordcounts_in/ \
--     -p PMI_OUTPUT_DIR=dir_to_save_pmi_calculations_in/ get_pmi_from_start_to_end.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

REGISTER 'get_pmi_from_start_to_end_udfs.py' USING jython AS religioussnippetsudfs;
DEFINE docmakingudfnonoverlapping religioussnippetsudfs.docmakingudfnonoverlapping();

-- would also work if run on all page captures, but this step is so time-consuming that it's much better to run it on a pre-filtered set of documents

-- note to self: provided this argument as dir_with_all_religious_captures/

instance = LOAD '$FILTERED_RELIGIOUS_CAPTURE_DIR' USING PigStorage('\t') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             document:chararray);

instance = FOREACH instance GENERATE
                               FLATTEN(
                                  docmakingudfnonoverlapping(document)
                               ),
                               URL AS URL:chararray,
                               surt AS surt:chararray,
                               checksum AS checksum:chararray,
                               date AS date:chararray,
                               code AS code:chararray,
                               title AS title:chararray,
                               description AS description:chararray;

-- since this is a time-consuming step, we save the intermediate results in case we want to re-run any calculations later

-- note to self: provided this argument as religious_snippets/ OR policy_religious_captures_docsnippets_nonoverlapping/

STORE instance INTO '$RELIGIOUS_SNIPPETS_DIR' USING PigStorage('\t');

all_cooccurring_words = FOREACH instance GENERATE FLATTEN(TOKENIZE(text, ' ')) AS word:chararray;

religious_cooccurring_wordcounts = FOREACH (GROUP all_cooccurring_words BY word) GENERATE FLATTEN(group) AS cooccurring_word:chararray,
                                                                                          COUNT(all_cooccurring_words) AS religious_wordcount:long;

-- note to self: provided this argument as dir_with_all_preprocessed_captures/ , although
-- caveat: this was the directory that I never actually ended up making (took a circuitous
-- code route instead)

full_instance = LOAD '$ALL_PREPROCESSED_CAPTURES_DIR' USING PigStorage('\t') AS
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

all_words = FOREACH full_instance GENERATE FLATTEN(TOKENIZE(content, ' ')) AS word:chararray;

corpus_counts = FOREACH (GROUP all_words BY word) GENERATE FLATTEN(group) AS term:chararray,
                                                           COUNT(all_words) - 1 AS wordcount_minus_1:long;

-- we save the versions of wordcounts with 1 subtracted from them to save memory, as this screens out any words appearing only once from being written to file

corpus_counts = FILTER corpus_counts BY wordcount_minus_1 > 0;

-- since this is a relatively time-consuming step, we save the intermediate results in case we want to re-run any calculations later

-- note to self: provided this argument as lowercaseword_corpuscounts/ OR lowercaseword_policydoccounts/

STORE corpus_counts INTO '$CORPUSWIDE_WORDCOUNTS' USING PigStorage('\t');

religious_cooccurring_wordcounts = JOIN religious_cooccurring_wordcounts BY cooccurring_word LEFT OUTER, corpus_counts BY term;

religious_cooccurring_wordcounts = FOREACH religious_cooccurring_wordcounts GENERATE religious_cooccurring_wordcounts::cooccurring_word AS word:chararray,
                                                                                     religious_cooccurring_wordcounts::religious_wordcount AS religious_wordcount:long,
                                                                                     (corpus_counts::wordcount_minus_1 == 0 ? 1 : corpus_counts::wordcount_minus_1 + 1) AS corpus_wordcount:long;

religious_cooccurring_wordcounts_with_pmi = FOREACH religious_cooccurring_wordcounts GENERATE word AS word,
                                                                                                     religious_wordcount AS religious_wordcount,
                                                                                                     corpus_wordcount AS corpus_wordcount,
                                                                                                     ((float) (religious_wordcount / 100000) / (float) ((corpus_wordcount + 10000000) / 100000)) AS pmi:float;

religious_cooccurring_wordcounts_with_pmi = ORDER religious_cooccurring_wordcounts_with_pmi BY pmi DESC;

-- note to self: provided this argument as pmi/

STORE religious_cooccurring_wordcounts_with_pmi INTO '$PMI_OUTPUT_DIR' USING PigStorage('\t');
