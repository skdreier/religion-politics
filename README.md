# Religion and Politics
## Lucy Lin, Sofia Serrano, Emily Kalah Gade, Sarah Dreier

## Running scripts

1. Copy the repository up to your personal workbench

2. For most scripts, running in a tmux window will be necessary to keep the program from quitting when your ssh session times out. If opening a tmux window, be sure to open it before doing the next step; otherwise, the changes that are supposed to be made to classpaths by that step won't persist for your script.

3. From the top-level directory of the repository, run the command

   ```
   source add_dependencies_to_classpath.sh
   ```

   (this will add the jar files in the lib directory to your classpath and pig_classpath)
   
### Running non-template pig script (i.e., ExtractCounts)

4. From the top-level directory of the repository, run some variation on the command

   ```
   pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/ -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ -p O_DATA_DIR=outputARC2/ -p O_DATA_DIR_2=outputARC2-2/ ExtractCounts_keywords.pig
   ```

   providing the local path from this directory to your desired pig script, and making sure that your provided values for O_DATA_DIR and O_DATA_DIR_2 are not already preexisting directories in the hadoop file system at `hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/`. (If, for example, `hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/outputARC2` already existed when the example command was run, the script would quit out for reasons related to "output validation.")
   
   (To see the contents of `hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/`, run the command
   
   ```
   hdfs dfs -ls hdfs://nn-ia.s3s.altiscale.com:8020/user/<your_workbench_username>/
   ``` 
   
   from any directory. Other unix commands can be run on files located there by changing `-ls` to a different command.)
   
### Running pig scripts from a template (i.e., get_cooccurrence_words)

4. From the top-level directory of the repository, run some variation on the command

   ```
   bash get_cooccurrence_words.sh 30 1000 cooccuroutput /dataset-derived/gov/parsed/arcs/bucket-0/ /dataset/gov/url-ts-checksum/
   ```

   For get_cooccurrence_words.sh, these are the five arguments in the order they're provided:
   
   * half window size: the number of words to take both before and after an appearance of a search term as "cooccurring" with that term
   * number of top results to output: for each search term (as well as the two aggregated result types, anysearchword and allsearchwords), the number of top-scoring cooccurring words to report
   * output directory name stub: the string to prepend to the directories of all the results files. Make sure that the directories starting with this string and ending in the provided search terms don't already exist in the hadoop file system, or hadoop will throw an error. Do not end this with /
   * I_PARSED_DATA: the full path on the hadoop file system to the input parsed data
   * CHECKSUM_DATA: the full path on the hadoop file system to the checksum data. (If not using checksum data, replace this argument with the string None)
   
   For get_keyword_counts.sh, these are the three arguments in the order they're provided:
   
   * output directory name (doubles as base of name of text file that will store aggregated results). Do not end this with /
   * I_PARSED_DATA: the full path on the hadoop file system to the input parsed data
   * CHECKSUM_DATA: the full path on the hadoop file system to the checksum data. (If not using checksum data, replace this argument with the string None)
   
   The bash script will first run a separate script to generate a pig script from the template in the repository with the provided search terms in the corresponding .txt file hard-coded in (for get_cooccurrence_words.sh, those are read from get_cooccurrence_words_words_to_search.txt). Then, the script will run that automatically generated script.
   
## Troubleshooting Issues

* A pig script sets up successfully, but then gets stuck at 0% completion for hours: after killing this job, check whether there's a phantom yarn thread running from a previous job, and if so, kill it.

   * From the workbench, run the command 
   
     ```
     yarn application -list
     ```
     and if there's an old thread running there that shouldn't be, run the command
     ```
     yarn application -kill <Application ID>
     ```