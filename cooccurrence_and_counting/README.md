## Running cooccurence/keyword-counting scripts

1. Copy the repository up to your personal workbench

2. Populate the text file corresponding to the script you're planning to run with the keywords or searchwords that you want to use. See the directions at the top of the file for details.

   Text file correspondences:
   
   * get_cooccurrence_words.sh: get_cooccurrence_words_words_to_search.txt
   * get_keyword_counts.sh: get_keyword_counts_keywords_to_count.txt
   * get_keyword_doc_counts.sh: get_keyword_doc_counts_keywords_to_count.txt

3. From inside the cooccurrence_and_counting directory of the repository, run some variation on a command calling a bash script within this directory. For example:

   ```
   bash get_cooccurrence_words.sh 30 1000 cooccuroutput /dataset-derived/gov/parsed/arcs/bucket-0/ /dataset/gov/url-ts-checksum/ False
   ```

   For get_cooccurrence_words.sh, these are the six arguments in the order they're provided:
   
   * half window size: the number of words to take both before and after an appearance of a search term as "cooccurring" with that term
   * number of top results to output: for each search term (as well as the two aggregated result types, anysearchword and allsearchwords), the number of top-scoring cooccurring words to report
   * output directory name stub: the string to prepend to the directories of all the results files. Make sure that the directories starting with this string and ending in the provided search terms don't already exist in the hadoop file system, or hadoop will throw an error. Do not end this with /
   * I_PARSED_DATA: EITHER the full path on the hadoop file system to the input parsed data (if skip_pig is False), OR the path stub that the two necessary directories of data on the local system have in common (i.e., /data/bucket0  to represent /data/bucket0-fulltext/ and /data/bucket0-sampledocfrequencies/)
   * CHECKSUM_DATA: the full path on the hadoop file system to the checksum data. (If not using checksum data, replace this argument with the string None)
   * skip_pig: True or False. Set to True if pig script referenced in get_cooccurrence_words.sh still needs to be run, or False if pig script has already been run and results are in files off the hdfs filesystem.
   
   For get_keyword_counts.sh or get_keyword_doc_counts.sh, these are the three arguments in the order they're provided:
   
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