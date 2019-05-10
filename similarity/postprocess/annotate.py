# postprocess.annotate

import common.disable_warnings
import common.configure_logging

import argparse
import json

from openpyxl import Workbook
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

    # TODO: consolidate w/write_spreadsheet in find_matches
    # (the vagaries of formatting, whee)
    output_path = '{}-annotated.xlsx'.format(args.output_prefix)
    write_spreadsheet(output_path, data)


def write_spreadsheet(path, data):
    wb = Workbook()
    ws = wb.active

    for q_info in data:
        ws.title = q_info['id']
        ws.append(['# query: {}'.format(q_info['query'])])

        header = ['score', 'sentence', 'url', 'checksum', 'date', 'party',
                  'religious']
        ws.append(header)
        for m in q_info['matches']:
            ws.append(m[k] for k in header)

        ws = wb.create_sheet()

    wb.save(path)


if __name__ == '__main__':
    main()
