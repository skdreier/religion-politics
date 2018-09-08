# documents.load

import common.disable_warnings

import itertools
import logging
import os

from common.utils import pbar_file_generator


MIN_DOC_LEN = 10

# metadata fields:
# * url
# * surturl
# * checksum
# * date
# * response code
# * title
# * description
#
# text field:
# * content
NUM_FIELDS = 8
URL_FIELD = 0
CHKSUM_FIELD = 2
DATE_FIELD = 3
TEXT_FIELD = 7


def load_dotgov_files(dir_):
    # progress bar modified from
    # https://github.com/tqdm/tqdm/wiki/How-to-make-a-great-Progress-Bar

    for filepath in pbar_file_generator(dir_):
        with open(filepath, 'r') as f:
            raw = f.read()

        # '\n' separated lines
        # '\u0001' separated fields per line
        for line in raw.split('\n'):
            fields = line.split('\u0001')

            if len(fields) != NUM_FIELDS:
                continue

            # keep url, checksum, date
            meta = (fields[URL_FIELD], fields[CHKSUM_FIELD],
                    fields[DATE_FIELD])

            text = fields[TEXT_FIELD].strip()

            if len(text) > MIN_DOC_LEN:
                yield text, meta



def load_query_files(dir_):
    for filepath in pbar_file_generator(dir_):
        with open(filepath, 'r') as f:
            raw = f.read()

        for line in raw.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            fields = line.split(',', 1)

            if len(fields) > 1:
                query_id = fields[0].strip()
                query = fields[1].strip()
                yield query, query_id

