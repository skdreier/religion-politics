-- The version of this file with TEMPLATE in the name is just a template; don't run this file,
-- run make_pig_script_from_template.py first (running get_filtered_religious_files.sh will do this for you).

-- After get_filtered_religious_files.pig has been generated, run the command

-- pig -p LATEST_RELIGIOUS_INPUT_DIR=/your/input/dir_with_latest_set_of_religious_files \
--     -p LATEST_FILTERED_OUTPUT_DIR=your_output_dir/ get_filtered_religious_files.pig


SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

-- note to self: for me, this argument should be provided as /user/sofias6/all_religious_captures2

instance = LOAD '$LATEST_RELIGIOUS_INPUT_DIR' USING PigStorage('\t') AS (URL:chararray,
                                                                         surt:chararray,
                                                                         checksum:chararray,
                                                                         date:chararray,
                                                                         code:chararray,
                                                                         title:chararray,
                                                                         description:chararray,
                                                                         document:chararray);

contains_matchword_without_caveats = FILTER instance BY
                                             STARTLINEREPEAT_ONLYNOCAVEATMATCHES_REGEXESPERLINE100
                                             document MATCHES INSERTPIGREGEXHERE
                                             ENDLINEREPEAT_ONLYNOCAVEATMATCHES_REGEXESPERLINE100

remaining = FILTER instance BY NOT(
                                  STARTLINEREPEAT_ONLYNOCAVEATMATCHES_REGEXESPERLINE100
                                  document MATCHES INSERTPIGREGEXHERE
                                  ENDLINEREPEAT_ONLYNOCAVEATMATCHES_REGEXESPERLINE100
                            );

contains_no_false_match_text_but_has_match = FILTER remaining BY NOT(
                                  STARTLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100
                                  document MATCHES INSERTPIGREGEXHERE
                                  ENDLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100
                            );

no_other_keywords_has_at_least_one_false_match = FILTER remaining BY
                                  STARTLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100
                                  document MATCHES INSERTPIGREGEXHERE
                                  ENDLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100

false_match_edited_out = FOREACH no_other_keywords_has_at_least_one_false_match GENERATE
                                  URL AS URL:chararray,
                                  surt AS surt:chararray,
                                  checksum AS checksum:chararray,
                                  date AS date:chararray,
                                  code AS code:chararray,
                                  title AS title:chararray,
                                  description AS description:chararray,
                                  document AS document:chararray,
                                  document AS edited_document:chararray;

STARTLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100
false_match_edited_out = FOREACH false_match_edited_out GENERATE
                                  URL AS URL:chararray,
                                  surt AS surt:chararray,
                                  checksum AS checksum:chararray,
                                  date AS date:chararray,
                                  code AS code:chararray,
                                  title AS title:chararray,
                                  description AS description:chararray,
                                  document AS document:chararray,
                                  REPLACE(edited_document, INSERTNOBOOKENDSPIGREGEXHERE, ' ') AS edited_document:chararray;

ENDLINEREPEAT_ONLYFALSEMATCHES_REGEXESPERLINE100

contains_true_match_besides_false_match = FILTER false_match_edited_out BY
STARTLINEREPEAT_ONLYMATCHESWITHCAVEATS_REGEXESPERLINE100
                                  edited_document MATCHES INSERTREGEXHERE
ENDLINEREPEAT_ONLYMATCHESWITHCAVEATS_REGEXESPERLINE100

contains_true_match_besides_false_match = FOREACH contains_true_match_besides_false_match GENERATE
                                  URL AS URL:chararray,
                                  surt AS surt:chararray,
                                  checksum AS checksum:chararray,
                                  date AS date:chararray,
                                  code AS code:chararray,
                                  title AS title:chararray,
                                  description AS description:chararray,
                                  document AS document:chararray;

religious_instance = UNION contains_matchword_without_caveats, contains_no_false_match_text_but_has_match, contains_true_match_besides_false_match;

religious_instance = ORDER religious_instance BY date;

-- note to self: for me, this argument was provided as all_religious_captures_filtered/

STORE religious_instance INTO '$LATEST_FILTERED_OUTPUT_DIR' USING PigStorage('\t');
