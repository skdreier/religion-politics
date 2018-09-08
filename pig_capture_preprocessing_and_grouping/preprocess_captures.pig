-- To run:
-- pig -p CAPTURE_DIR=/top_level/dir/containing_arcs_and_warcs_dirs -p PREPROCESSED_CAPTURE_DIR=an_output_dir/ \
--     preprocess_captures.pig

SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

REGISTER 'preprocessing_udfs.py' USING jython AS lowercase;
DEFINE fix_format lowercase.lowercase_and_add_space_bookends();

instance0 = LOAD '$CAPTURE_DIR/arcs/bucket-0/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance1 = LOAD '$CAPTURE_DIR/arcs/bucket-1/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance2 = LOAD '$CAPTURE_DIR/arcs/bucket-2/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance3 = LOAD '$CAPTURE_DIR/arcs/bucket-3/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance4 = LOAD '$CAPTURE_DIR/arcs/bucket-4/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance5 = LOAD '$CAPTURE_DIR/arcs/bucket-5/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance0w = LOAD '$CAPTURE_DIR/warcs/bucket-0/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance1w = LOAD '$CAPTURE_DIR/warcs/bucket-1/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance2w = LOAD '$CAPTURE_DIR/warcs/bucket-2/' USING PigStorage('\u0001') AS 
   (URL:chararray,
    surt:chararray,
    checksum:chararray,
    date:chararray,
    code:chararray,
    title:chararray,
    description:chararray,
    content:chararray);

instance = UNION instance0,
                 instance1, 
                 instance2, 
                 instance3, 
                 instance4, 
                 instance5, 
                 instance0w, 
                 instance1w, 
                 instance2w;

-- replace newlines, tabs, non-visible chars with spaces

instance = FOREACH instance GENERATE 
   URL AS URL:chararray,
   surt AS surt:chararray,
   checksum AS checksum:chararray,
   date AS date:chararray,
   code AS code:chararray,
   title AS title:chararray,
   description AS description:chararray,
   REPLACE(content, '[^\\p{Graph}]', ' ') AS content:chararray;
   
-- make text lowercase, prepend a space, append a space
-- (spaces are helpful in simplifying regexes run in later scripts)

instance = FOREACH instance GENERATE 
   URL AS URL:chararray,
   surt AS surt:chararray,
   checksum AS checksum:chararray,
   date AS date:chararray,
   code AS code:chararray,
   title AS title:chararray,
   description AS description:chararray,
   fix_format(content) AS content:chararray;

-- note to self: this arg was provided as preprocessed_docs/
                                     
STORE instance INTO '$PREPROCESSED_CAPTURE_DIR' USING PigStorage('\t');