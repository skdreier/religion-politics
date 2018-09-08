# postprocess.intersect_religion_docs

import common.configure_logging

import argparse
import csv
import json
import logging
import os

from collections import defaultdict
from common.utils import pbar_file_generator
from operator import itemgetter


def annotate(policy_matches, religion_dir):
    logging.info('Loading religion urls...')
    religion_files = pbar_file_generator(religion_dir)
    urls = extract_religion_urls(religion_files)

    logging.info('Finding policy-religion intersection...')
    policy_matches = take_intersection(policy_matches, urls)

    return policy_matches


def extract_religion_urls(religion_files):
    urls = set()

    for path in religion_files:
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                # fields: surt, checksum, url, date
                url_info = (row[2], row[1])
                urls.add(url_info)

    return urls


def take_intersection(matches, urls):
    for q_info in matches:
        for m in q_info['matches']:
            url_info = (m['url'], m['checksum'])

            if url_info in urls:
                m['religious'] = True
            else:
                m['religious'] = False

    return matches
