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
DEFINE docmakingudfnonoverlapping paddingfuncs.docmakingudfnonoverlapping();

-- if loading from a directory where a space hasn't already been added to either end of the document,
-- then call pad_str on document to add those

-- all_religious_captures_filtered_2ndtime

instance = LOAD '/user/sofias6/all_religious_captures_filtered_notinflated/' USING PigStorage('\t') AS (URL:chararray,
                                                                                    surt:chararray,
                                                                                    checksum:chararray,
                                                                                    date:chararray,
                                                                                    code:chararray,
                                                                                    title:chararray,
                                                                                    description:chararray,
                                                                                    document:chararray);

term_specific_doc_snippet = FOREACH instance GENERATE
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

STORE term_specific_doc_snippet INTO 'all_religious_captures_docsnippets_nonoverlapping/' USING PigStorage('\t');