instance = LOAD '/user/sofias6/full_lowercased_policy_docs2/' USING PigStorage('\t') AS (URL:chararray,
                                                                             surt:chararray,
                                                                             checksum:chararray,
                                                                             date:chararray,
                                                                             code:chararray,
                                                                             title:chararray,
                                                                             description:chararray,
                                                                             content:chararray);

for_counting = GROUP instance ALL;

for_counting = FOREACH for_counting GENERATE COUNT(instance) AS counted;

DUMP for_counting;