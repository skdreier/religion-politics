# postprocess.compute_party_ratios

import common.disable_warnings
import common.configure_logging

import argparse
import json

from collections import defaultdict
from itertools import product
from openpyxl import Workbook
from urllib.parse import urlparse


def load_name_maps():
    parties = ['dem', 'rep']
    sites = ['senate', 'house']

    print('loading house')
    with open('party/house_people_modified.json', 'r') as f:
        house = json.load(f)

    print('loading senate')
    with open('party/senate_people_modified.json', 'r') as f:
        senate = json.load(f)

    return {
        'house': house,
        'senate': senate
    }


def _lookup_name(name_map, name, year):
    if name in name_map:
        parties = set()
        people = name_map[name]
        for p in people:
            #if year < p['start_year'] or year > p['end_year']:
            #    continue

            parties.add(p['party'])

        if len(parties) > 1:  # we can't resolve this
            #print('conflict: {}, {}'.format(name, year))
            return 'conflict'

        elif len(parties) == 1:
            return list(parties)[0]

    return None


def get_party_from_url(name_maps, url, year, warnings):
    parsed = urlparse(url)
    parts = parsed.netloc.split('.')

    name = parts[0]
    if name == 'www':
        name = parts[1]

    site = parts[-2]  # last part is .gov, and senate/house comes before that

    if site in name_maps:
        name_map = name_maps[site]

        party = _lookup_name(name_map, name, year)
        if party:
            if party == 'conflict':
                warnings['conflict'][name].append(year)

            return party

        # very occasionally, this might be located in house.gov/lastname
        path = parsed.path
        parts = path.split('/')

        if len(parts) > 1:
            first = parts[1]  # skip first '/'

            party = _lookup_name(name_map, first[1:], year)
            if party:
                if party == 'conflict':
                    warnings['conflict'][name].append(year)

                return party

    # we don't have it
    warnings['notfound'][name] += 1
    return 'unk'  # maybe not a person, but double check


def add_party_info(data, name_maps):
    warnings = {
        'notfound': defaultdict(int),
        'conflict': defaultdict(list)
    }
    for q_data in data:
        for m in q_data['matches']:
            year = int(str(m['date'])[:4])  # :/
            m['party'] = get_party_from_url(name_maps, m['url'], year, warnings)

    return data, warnings


def aggregate_parties(data):
    for q_data in data:
        q_data['dem'] = 0
        q_data['rep'] = 0
        q_data['unk'] = 0
        q_data['conflict'] = 0

        for m in q_data['matches']:
            party = m['party']
            q_data[party] += 1

    return data


def write_ratios(path, data):
    output = []
    for q_data in data:
        qid = q_data['id']
        dem = q_data['dem']
        rep = q_data['rep']
        unk = q_data['unk']
        conflict = q_data['conflict']
        query = q_data['query']

        output.append('{}\t{}/{}/{}/{}\t{}'.format(qid, dem, rep, unk, conflict, query))

    with open(path, 'w') as f:
        f.write('\n'.join(output))


# TODO: merge w/the one in find_matches.py
def write_spreadsheet(wb_path, data):
    wb = Workbook()
    ws = wb.active

    for q_data in data:
        ws.title = q_data['id']

        query = q_data['query']
        ws.append(['# query: {}'.format(query)])

        header = ['score', 'sentence', 'party', 'url', 'checksum', 'date']
        ws.append(header)
        for m in q_data['matches']:
            ws.append(m[k] for k in header)

        ws = wb.create_sheet()

    wb.save(wb_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_path')
    ap.add_argument('output_prefix')
    args = ap.parse_args()

    name_maps = load_name_maps()

    with open(args.input_path, 'r') as f:
        data = json.load(f)

    data, warnings = add_party_info(data, name_maps)
    data = aggregate_parties(data)

    ratio_path = '{}-ratios.txt'.format(args.output_prefix)
    write_ratios(ratio_path, data)

    with open('{}-conflicts.json'.format(args.output_prefix), 'w') as f:
        json.dump(warnings['conflict'], f, indent=2)

    with open('{}-notfound.txt'.format(args.output_prefix), 'w') as f:
        names = sorted(list(warnings['notfound'].keys()))
        f.write('\n'.join(names))

    wb_path = '{}-parties.xlsx'.format(args.output_prefix)
    write_spreadsheet(wb_path, data)


if __name__ == '__main__':
    main()
