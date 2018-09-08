# postprocess.annotate

import common.disable_warnings
import common.configure_logging

import argparse
import json

from postprocess import party_affiliation
from postprocess import religion_intersect


RELIGION_DIR = '/m-pinotHD/sofias6/dotgov/all_religious_captures_urls/'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_path')
    ap.add_argument('output_prefix')
    args = ap.parse_args()

    with open(args.input_path, 'r') as f:
        data = json.load(f)

    data = party_affiliation.annotate(data, args.output_prefix)
    data = religion_intersect.annotate(data, RELIGION_DIR)

    output_path = '{}-annotated.json'.format(args.output_prefix)
    with open(output_path, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    main()
