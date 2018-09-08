For all scripts, sample usage is described in comments at the top.

NOTE: ANY OUTPUT DIRECTORY PROVIDED TO PIG SCRIPT MUST NOT EXIST YET, OTHERWISE PIG WILL THROW AN ERROR.

## Preprocessing page captures

Run `preprocess_captures.pig`.

## Filtering preprocessed captures by keyword match

1. If desired, modify `../all_religious_words.txt` to contain a different set of keywords to search

2. Run `get_initialized_religious_files.sh`

3. Optionally, run

   * `sampl`../misc_bash/download_hdfs_files.sh` (might need to modify if HDFS system being used is accessed locally, not by ssh)e_preprocessed_captures_from_directory.pig`
   *
      * With the appropriate arguments, copies the sampled captures from the HDFS system to the local one
   * `collect_all_keyword_contexts_from_sampled_captures.py`
      * These contexts can then be manually inspected for false-match phrases to add to `../all_religious_words.txt` using #
   * `get_filtered_religious_files.sh`

   as many times as desired, or until the sampled page captures are no longer turning up false matches.

## Filtering preprocessed captures by capture match to URL

Run `get_capture_subset_by_url.pig`.

(For the work described in the paper, this was done to set aside page captures that had comes up as particularly strong policy matches.)

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