-- Downloads all files in the senate.gov and house.gov domains from
-- the archive.

-- TO RUN:
--     pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-4/ \
--         -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ \
--         -p O_DATA_DIR=outputARC4/ \
--         -p O_DATA_DIR_2=outputARC4-2/ \
--         FilterFiles.pig


-- hadoop magic memory values
SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;

-- register library calls
REGISTER lib/porky-abbreviated.jar;
REGISTER lib/webarchive-commons-1.1.7.jar;
DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- (\ are doubly escaped b/c one of them will be stripped away)
%declare UNPRINTABLE '[^\\\\p{Graph}]'


-- load data
Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader()
            AS (key:chararray, value:chararray);
Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];


-- get rid of entries with errors
Archive = FILTER Archive BY m#'errorMessage' is null;

-- pull out fields of interest
ExtractedFields = FOREACH Archive GENERATE
    m#'url'                                         AS src:chararray,
    SURTURL(m#'url')                                AS surt:chararray,
    REPLACE(m#'digest', 'sha1:', '')                AS checksum:chararray,
    SUBSTRING(m#'date', 0, 8)                       AS date:chararray,
    REPLACE(m#'code', '$UNPRINTABLE', ' ')          AS code:chararray,
    REPLACE(m#'title', '$UNPRINTABLE', ' ')         AS title:chararray,
    REPLACE(m#'description', '$UNPRINTABLE', ' ')   AS description:chararray,
    REPLACE(m#'content', '$UNPRINTABLE', ' ')       AS content:chararray;


-- filter by urls of interest
Filtered = FILTER ExtractedFields BY surt MATCHES 'gov,senate.*'
                                  OR surt MATCHES 'gov,house.*';


STORE Filtered INTO '$O_DATA_DIR' USING PigStorage('\u0001');
