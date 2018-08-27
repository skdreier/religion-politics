# parse_party_lists.py

# take raw lists of senators & representatives (by party) from
    # http://bioguide.congress.gov/biosearch/biosearch1.asp
# and construct a seed dictionary of url fragments, mapped to
# person/party

import json

from collections import defaultdict

def extract_people(file_info_list, output_path):
    people = defaultdict(list)

    for input_path, party in file_info_list:
        with open(input_path, 'r') as f:
            lines = f.readlines()

        i = 2
        while i < len(lines):  # ignore headers
            # LASTNAME, Firstname is first thing in a new person's entry
            last_name = lines[i].split(',', 1)[0].lower()
            first_name = lines[i].split(' ', 2)[1].lower()

            # get the first year they were in office (minus the aprens)
            i += 1
            start_year = int(lines[i].split('-')[0][1:])

            # find the last date entry for this person
            while (i < len(lines) and
                (lines[i].startswith('Senator') or lines[i].startswith('(')
                    or lines[i].startswith('Representative'))):
                i += 1

            # get the end (minus the parens)
            end_year = int(lines[i-1].split('-')[1][:-2])
            if end_year < 1992:
                continue

            people[last_name].append({
                'first_name': first_name,
                'start_year': start_year,
                'end_year': end_year,
                'party': party
            })

    with open(output_path, 'w') as f:
        json.dump(people, f, indent=2)

    return people


def main():
    # raw data copy/pasted from
    # http://bioguide.congress.gov/biosearch/biosearch1.asp
    senate_info = [
        ('raw_senate_dems.txt', 'dem'),
        ('raw_senate_reps.txt', 'rep'),
    ]
    house_info = [
        ('raw_house_reps.txt', 'rep'),
        ('raw_house_dems.txt', 'dem'),
    ]

    extract_people(senate_info, 'senate_people.json')
    extract_people(house_info, 'house_people.json')


if __name__ == '__main__':
    main()
