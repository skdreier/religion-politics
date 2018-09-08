For all scripts, sample usage is described in comments at the top.

If you haven't already, first preprocess the captures and set aside religious-match (or, more generally, keyword-match) captures as described in `pig_capture_preprocessing_and_grouping/`.

NOTE: ANY OUTPUT DIRECTORY PROVIDED TO PIG SCRIPT MUST NOT EXIST YET, OTHERWISE PIG WILL THROW AN ERROR.

## Getting and plotting dates of captures by month

1. If you haven't done so already, you'll need to have run `get_pmi_from_start_to_end.pig` in the `cooccurrence_and_counting/` directory at least once, to generate the set of religious snippets. (Alternately, you could modify `get_nonchecksum_dates.pig` to take in the religious data in normal capture format, so that you could just use your filtered directory of religious captures instead.)

2. Run `get_nonchecksum_dates.pig`

3. Run `date_binner_by_string.pig` to get counts of dates binned by month

4. Run `../misc_bash/download_hdfs_files.sh` to get local, python-workable copies of the binned date files (might need to modify if HDFS system being used is accessed locally, not by ssh)

5. Run `condense_dir_files_into_single_file.py` on the downloaded directories of binned dates and rename the directories to work with the names listed in `make_plots.py`

6. Run `make_plots.py`

## Troubleshooting issues

* A pig script sets up successfully, but then gets stuck at 0% completion for hours: after killing this job, check whether there's a phantom yarn thread running from a previous job, and if so, kill it.

   * From the workbench, run the command

     ```
     yarn application -list
     ```
     and if there's an old thread running there that shouldn't be, run the command
     ```
     yarn application -kill <Application ID>