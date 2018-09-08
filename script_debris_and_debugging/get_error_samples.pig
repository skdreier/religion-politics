SET default_parallel 100;
SET mapreduce.map.memory.mb 8192;
SET mapreduce.reduce.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER ../lib/porky-abbreviated.jar;
REGISTER ../lib/webarchive-commons-1.1.7.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to.

REGISTER 'get_religious_snippets_udfs.py' USING jython AS paddingfuncs;

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
-- I haven't really figured out why this is helpful, but it does help with using existing scripts because the
-- ones internet archive wrote use this format

DEFINE SURTURL org.archive.porky.SurtUrlKey();
DEFINE docmakingudf paddingfuncs.docmakingudf();


instance0 = LOAD '/user/lucylin/arcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1 = LOAD '/user/lucylin/arcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2 = LOAD '/user/lucylin/arcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance3 = LOAD '/user/lucylin/arcs/bucket-3/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance4 = LOAD '/user/lucylin/arcs/bucket-4/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance5 = LOAD '/user/lucylin/arcs/bucket-5/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance0w = LOAD '/user/lucylin/warcs/bucket-0/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance1w = LOAD '/user/lucylin/warcs/bucket-1/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance2w = LOAD '/user/lucylin/warcs/bucket-2/' USING PigStorage('\u0001') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

instance_full = UNION instance0, instance1, instance2, instance3, instance4, instance5, instance0w, instance1w, instance2w;

instance_full = FILTER instance_full BY surt MATCHES 'gov,senate,src./public/index.cfm..fuseaction=states.home.istextonly=true.state_id=42';
instance_full = FILTER instance_full BY checksum MATCHES 'BR4PYXVAJGH54XHC3FWD7OA2CSV6WAUT';

instance_full_words = FOREACH instance_full GENERATE FLATTEN(TOKENIZE(content, ' ')) AS word:chararray;
ifw = FOREACH (GROUP instance_full_words BY word) GENERATE FLATTEN(group) AS word:chararray,
                                                     COUNT(instance_full_words) AS count:long;

DUMP ifw;

