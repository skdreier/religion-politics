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

