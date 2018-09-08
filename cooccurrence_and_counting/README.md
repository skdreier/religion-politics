For all scripts, sample usage is described in comments at the top.

If you haven't already, first preprocess the captures and set aside religious-match (or, more generally, keyword-match) captures as described in `pig_capture_preprocessing_and_grouping/`.

NOTE: ANY OUTPUT DIRECTORY PROVIDED TO PIG SCRIPT MUST NOT EXIST YET, OTHERWISE PIG WILL THROW AN ERROR.

## Running PMI calculations

Run `get_pmi_from_start_to_end.pig`.

(I didn't get around to turning this script into a template, so if you want to change the set of keywords and/or what counts as a false match when creating the match snippets, you'd need to manually edit the first few lines of `get_pmi_from_start_to_end_udfs.py`.)

(If running PMI calculations for a second time using the same corpus and set of religious snippets, consider modifying the script to take advantage of the intermediate output generated to save time on the first run.)

## Counting the number of preprocessed page captures in a directory

Run `count_number_of_captures_in_dir.pig`.

## Getting the number of counts for loose keyword matches

1. If desired, modify `non_pig_loose_keyword_match.txt` to contain different keywords

2. Run `../misc_bash/download_hdfs_files.sh` to get local, python-workable copies of the HDFS files to check (might need to modify if HDFS system being used is accessed locally, not by ssh)

3. Run `non_pig_keyword_count.py`

## Counting the number of captures in an HDFS directory

Run `count_number_of_captures_in_dir.pig`

## Getting document frequencies for all words appearing in directory

1. Run `../misc_bash/download_hdfs_files.sh` to get local, python-workable copies of the HDFS files to use while calculating (might need to modify if HDFS system being used is accessed locally, not by ssh)

2. Run `collect_word_frequencies_from_directory.py` with `Doc` as third argument

## Getting full count of all words appearing in directory

1. Run `../misc_bash/download_hdfs_files.sh` to get local, python-workable copies of the HDFS files to use while calculating (might need to modify if HDFS system being used is accessed locally, not by ssh)

2. Run `collect_word_frequencies_from_directory.py` with `Corpus` as third argument

## Troubleshooting issues

* A pig script sets up successfully, but then gets stuck at 0% completion for hours: after killing this job, check whether there's a phantom yarn thread running from a previous job, and if so, kill it.

   * From the workbench, run the command 
   
     ```
     yarn application -list
     ```
     and if there's an old thread running there that shouldn't be, run the command
     ```
     yarn application -kill <Application ID>
     ```