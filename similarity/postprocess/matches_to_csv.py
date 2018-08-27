# transform matches.json output into csv (to upload to hdfs for sofia)

import argparse
import csv
import json


def get_match_list(data):
    for q_data in data:
        # ignore the query itself
        for m in q_data['matches']:
             yield (m['url'], m['checksum'], m['date'], m['sentence'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_json')
    ap.add_argument('output_csv')
    args = ap.parse_args()

    with open(args.input_json, 'r') as f:
        data = json.load(f)

    matches = get_match_list(data)

    with open(args.output_csv, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(matches)


if __name__ == '__main__':
    main()
