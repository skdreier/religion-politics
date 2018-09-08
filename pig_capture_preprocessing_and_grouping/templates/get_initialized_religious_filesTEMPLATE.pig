-- The version of this file with TEMPLATE in the name is just a template; don't run this file,
-- run make_pig_script_from_template.py first (running get_initialized_religious_files.sh will do this for you).

-- After get_initialized_religious_files.pig has been generated, run the command

-- pig -p ALL_PREPROCESSED_CAPTURES_DIR=/your/input/dir_with_latest_set_of_religious_files \
--     -p LATEST_FILTERED_OUTPUT_DIR=your_output_dir/ get_filtered_religious_files.pig


SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

-- note to self: for me, this argument should be provided as /user/sofias6/prelim_religious_captures
-- (although when running this code in July/August, this directory would have been skipped)

instance = LOAD '$ALL_PREPROCESSED_CAPTURES_DIR' USING PigStorage('\t') AS (URL:chararray,
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

contains_matchword_with_caveats = FILTER remaining BY
                                        STARTLINEREPEAT_ONLYMATCHESWITHCAVEATS_REGEXESPERLINE100
                                        document MATCHES INSERTPIGREGEXHERE
                                        ENDLINEREPEAT_ONLYMATCHESWITHCAVEATS_REGEXESPERLINE100

-- note to self: for me, this argument was provided as all_religious_captures2/

prelim_captures = UNION contains_matchword_without_caveats, contains_matchword_with_caveats;

STORE prelim_captures INTO '$PRELIM_OUTPUT_DIR' USING PigStorage('\t');
