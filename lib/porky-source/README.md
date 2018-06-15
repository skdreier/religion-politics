## Porky source code

This code is almost entirely taken from the ia-porky directory of Vinay Goel's archive-analysis repository (https://github.com/vinaygoel/archive-analysis), and is only lightly edited and/or reorganized.

## Compiling a new jar file with porky classes

If including files that are currently in not_included, they will need to be copied back into included_in_porky-abbreviated/org/archive/porky, and there may be other external jar files required as well. Instructions from here on will be given for compiling a new porky jar file (to replace porky-abbreviated.jar in lib) from only the source files in included_in_porky-abbreviated.

First, make any desired changes to the .java source files in included_in_porky-abbreviated/org/archive/porky. (Before continuing on and compiling the code, also make sure that your JDK version is 8 or lower; anything higher currently throws an error on the server with the data.) Then, from lib, follow the correct set of directions for your system.

### If pig and hadoop already installed on local system

```
cd included_in_porky-abbreviated
javac -cp porky-abbreviated.jar -classpath ../../lucene-core-7.3.1.jar:../../org.json-20161124.jar:../../webarchive-commons-1.1.7.jar org/archive/porky/*.java
jar -cf porky-abbreviated.jar org/archive/porky/*.class
```

### If pig and hadoop are not installed

In this case, before running anything from the command line, you'll need jar files containing class files for the all the pig and hadoop classes imported in the porky source files. Downloading a jar file from each of the following three links will cover all of the required classes:

1. http://www.apache.org/dyn/closer.cgi/pig (Apache Pig)

2. http://www.apache.org/dyn/closer.cgi/hadoop/common (Apache Hadoop Common)

3. https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-mapreduce-client-core (Apache Hadoop MapReduce)

Place the downloaded jar files in lib. Now:

```
cd included_in_porky-abbreviated
javac -cp porky-abbreviated.jar -classpath ../../lucene-core-7.3.1.jar:../../<name_of_downloaded_pig_jar>:../../<name_of_downloaded_hadoop_common_jar>:../../org.json-20161124.jar:../../<name_of_downloaded_hadoop_mapreduce_jar>:../../webarchive-commons-1.1.7.jar org/archive/porky/*.java
jar -cf porky-abbreviated.jar org/archive/porky/*.class
```

The new porky-abbreviated.jar file is now in the included_in_porky-abbreviated/ directory.
