lucene_path=:lib/lucene-core-7.3.1.jar
json_path=:lib/org.json-20161124.jar
web_archive_path=:lib/webarchive-commons-1.1.7.jar
PIG_CLASSPATH=$PIG_CLASSPATH$lucene_path$json_path$web_archive_path
CLASSPATH=$CLASSPATH$lucene_path$json_path$web_archive_path