# assumes tab-delimited output files, with one document appearing per line, with the text of the
# document appearing as the last field in any given line

import sys
import os
import re
import multiprocessing
from math import ceil
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid

input_dir = sys.argv[1]

default_num_multiprocessing_threads = 8


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


def make_loose_regex(keyword):
    regex = '(?:'
    for letter in keyword:
        if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                or letter == ')'):
            regex += '\\'
        regex += letter
    regex += ')'
    return regex


def make_full_loose_regex_expression(all_keywords):
    regex = ''
    for keyword in all_keywords:
        regex += make_loose_regex(keyword) + "|"
    regex = regex[:-1]
    return regex


def get_list_of_text_from_file(filename):
    texts = []
    # we assume that the title doesn't start with a digit; if it does, the leading string of digits
    # will be removed
    with open(filename, "r") as f:
        all_lines = f.readlines()
    for line in all_lines:
        line = line.strip().lower()
        if line == '':
            continue
        line = line.split('\t')
        doc = line[-1]
        texts.append(doc)
    return texts


def get_matches(file_index):
    print("Starting work on file " + str(file_index + num_already_covered + 1) + " / " + str(len(all_filenames)))
    filename = all_filenames[file_index + num_already_covered]
    docs = get_list_of_text_from_file(filename)

    for doc in docs:
        match_inds = [(m.start(0), m.end(0)) for m in loose_match_searcher.finditer(doc)]
        reject_match_inds = [(m.start(0), m.end(0)) for m in reject_match_searcher.finditer(doc)]
        for match_ind_pair in match_inds:
            # first find out whether this is an exact match or not-- if not, no need to bother with any
            # further checking
            match_start = match_ind_pair[0]
            match_end = match_ind_pair[1]
            is_tight_match = ((match_end == len(doc) or not doc[match_end].isalpha()) and
                              (match_start == 0 or not doc[match_start - 1].isalpha()))
            if is_tight_match:
                # then it had better be contained in a reject_match_inds pair
                is_a_reject = False
                for reject_match_ind_pair in reject_match_inds:
                    if reject_match_ind_pair[0] <= match_ind_pair[0] and reject_match_ind_pair[1] >= match_ind_pair[1]:
                        is_a_reject = True
                        break
                if not is_a_reject:
                    print("PROBLEM DOC:")
                    print(doc)
                    print("Found a non-reject match for " + str(doc[match_ind_pair[0]: match_ind_pair[1]]))
                    exit(1)


def try_pool(num_threads):
    global num_already_covered
    try:
        pool = multiprocessing.Pool(processes=num_threads)
        list_of_wordcount_dicts = pool.map(get_matches, range(num_threads))
        num_already_covered += num_threads
    except:
        pool.close()
        return False
    pool.close()
    return list_of_wordcount_dicts


keywords, strs_to_avoid = get_keywords_and_keywords_strs_to_avoid("all_religious_words.txt")
phrases_to_reject = []
for key in strs_to_avoid.keys():
    phrases_to_reject += strs_to_avoid[key]
reject_match_searcher = re.compile(make_full_loose_regex_expression(phrases_to_reject))
loose_match_searcher = re.compile(make_full_loose_regex_expression(keywords))
all_filenames = get_list_of_all_files_in_dir(input_dir)
num_already_covered = 0
num_batches_to_run = int(ceil(len(all_filenames) / default_num_multiprocessing_threads))


master_dicts = [{}, {}, {}, {}]
num_docs_w_loose_text_match = 0
num_docs_w_tight_text_match = 0


for batch in range(num_batches_to_run):
    got_results = False
    latest_num_threads = default_num_multiprocessing_threads
    while not got_results:
        got_results = try_pool(latest_num_threads)
        if not got_results:
            latest_num_threads = int(latest_num_threads / 2)
            if latest_num_threads < 1:
                print("Didn't work even with a single thread. Exiting now.")
                exit(1)
                    
                    
print("Successfully completed test! All religious matches found were rejects.")
