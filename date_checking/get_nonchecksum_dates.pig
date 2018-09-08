-- With the current version of the code, this should only be run after get_pmi_from_start_to_end.pig
-- (in cooccurrence_and_counting) has already been run, since that's the script that is now
-- responsible for generating the HDFS directory of religious snippets.

-- To run:
-- pig -p ALL_PREPROCESSED_CAPTURES_DIR=/path/to/preprocessed/captures/dir/ \
--     -p ALL_NONCHECKSUM_CAPTURES_DATES=all_dates_output_dir/ \
--     -p RELIGIOUS_SNIPPETS_DIR=/path/to/snippets/producedby/get_pmi_from_start_to_end/ \
--     -p RELIGIOUS_NONCHECKSUM_CAPTURES_DATES=religious_dates_output_dir \
--     get_nonchecksum_dates.pig

-- note to self: since this was the directory I didn't make, this "argument" was actually provided
-- as the full /user/lucylin/(w)arcs/bucket-(0-5)/ and then a UNION

instance = LOAD '$ALL_PREPROCESSED_CAPTURES_DIR' USING PigStorage('\t') AS (URL:chararray,
                                                                            surt:chararray,
                                                                            checksum:chararray,
                                                                            date:chararray,
                                                                            code:chararray,
                                                                            title:chararray,
                                                                            description:chararray,
                                                                            content:chararray);

instance = FOREACH instance GENERATE date AS date:chararray,
                                     URL AS URL:chararray,
                                     surt AS surt:chararray,
                                     checksum AS checksum:chararray;

-- if you wanted to add checksum data, this would be the place to do it

instance = DISTINCT instance;

-- note to self: provided this argument as all_house_senate_nonchecksum_dates/

STORE instance INTO '$ALL_NONCHECKSUM_CAPTURES_DATES' USING PigStorage('\t');

-- note to self: provided this argument as /user/sofias6/all_religious_captures_docsnippets_nonoverlapping

instance = LOAD '$RELIGIOUS_SNIPPETS_DIR' USING PigStorage('\t') AS (searchterm:chararray,
                                                                     text:chararray,
                                                                     URL:chararray,
                                                                     surt:chararray,
                                                                     checksum:chararray,
                                                                     date:chararray,
                                                                     code:chararray,
                                                                     title:chararray,
                                                                     description:chararray);

instance = FOREACH instance GENERATE date AS date:chararray,
                                     URL AS URL:chararray,
                                     surt AS surt:chararray,
                                     checksum AS checksum:chararray;

instance = DISTINCT instance;

-- if you wanted to add checksum data, this would be the place to do it

-- note to self: provided this argument as religious_house_senate_nonchecksum_dates/

STORE instance INTO '$RELIGIOUS_NONCHECKSUM_CAPTURES_DATES' USING PigStorage('\t');
