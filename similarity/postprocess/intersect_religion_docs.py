# postprocess.intersect_religion_docs

import argparse
import csv
import json
import os

from collections import defaultdict
from common.utils import pbar_file_generator
from operator import itemgetter


def extract_policy_urls(matches):
    urls_by_policy = defaultdict(set)

    for q_info in matches:
        policy_type = q_info['id'].split('_', 1)[0]

        for m in q_info['matches']:
            urls = urls_by_policy[policy_type]
            urls.add((m['url'], m['date']))

    return urls_by_policy


def take_intersection(religion_files, policy_urls):
    relpol_matches = defaultdict(set)

    print_x = True
    for path in religion_files:
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                # surt, checksum, url, date
                url_info = (row[2], row[3])

                for policy_type, urls in policy_urls.items():
                    if url_info in urls:
                        relpol_matches[policy_type].add(url_info)

    return relpol_matches


def write_output(matches, output_dir):
    for policy_type, urls in matches.items():
        lines = ['\t'.join(url_info) for url_info in
                 sorted(urls, key=itemgetter(1))]

        path = os.path.join(output_dir,
                            'relpol-intersection-{}.txt'.format(policy_type))
        with open(path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('religion_dir')
    ap.add_argument('policy_match_file')
    ap.add_argument('output_dir')
    args = ap.parse_args()

    religion_files = pbar_file_generator(args.religion_dir)

    with open(args.policy_match_file) as f:
        policy_matches = json.load(f)

    policy_urls = extract_policy_urls(policy_matches)
    relpol_matches = take_intersection(religion_files, policy_urls)

    write_output(relpol_matches, args.output_dir)


if __name__ == '__main__':
    main()
