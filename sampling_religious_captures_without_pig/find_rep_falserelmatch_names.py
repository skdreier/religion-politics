# finds names of House Representatives or Senators whose names will trigger false religious matches

from glob import glob
import re
from pull_out_all_religious_matches_with_local_context import make_regex, get_list_of_keywords_and_exceptions


filename_of_keywords = '../all_religious_words.txt'
dir_of_raw_rep_files = '../similarity/party/'

keywords = get_list_of_keywords_and_exceptions(filename_of_keywords)
full_regex = '|'.join([make_regex(word_exceptions[0], word_exceptions[1]) for word_exceptions in keywords])
full_regex = re.compile(full_regex)

for filename in glob(dir_of_raw_rep_files + 'raw_*'):
    list_of_matches = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.lower()
            split_line = line.split(' ')
            if not split_line[0].endswith(','):
                continue  # it's not a line with a representative's name
            if full_regex.match(line) is not None:
                list_of_matches.append(line.strip())
    if len(list_of_matches) > 0:
        print(filename[filename.rfind('/') + 1:] + ':')
        for match in list_of_matches:
            print('\t' + match)
