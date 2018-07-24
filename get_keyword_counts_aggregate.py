import sys
import os
import re
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid
from make_pig_script_from_template import make_keyword_tuples

results_dir = 'script_output/'
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
output_filename = results_dir + sys.argv[1] + ".txt"
total_num_files = str(sys.argv[2])

already_loaded_in_previous_file = False
something_changed_in_file = False


def merge_match_lists(new_match_list, aggregated_match_list):
    no_overlap_in_matches = True
    new_list_pointer = 0
    big_list_pointer = 0
    while new_list_pointer < len(new_match_list):
        if big_list_pointer >= len(aggregated_match_list):
            while new_list_pointer < len(new_match_list):
                aggregated_match_list.append(new_match_list[new_list_pointer])
                new_list_pointer += 1
            break
        else:
            if aggregated_match_list[big_list_pointer][0] >= new_match_list[new_list_pointer][0]:
                aggregated_match_list.insert(big_list_pointer, new_match_list[new_list_pointer])
                new_list_pointer += 1
        big_list_pointer += 1
    for i in range(len(aggregated_match_list) - 1):
        if aggregated_match_list[i][1] > aggregated_match_list[i + 1][0]:
            no_overlap_in_matches = False
    return no_overlap_in_matches


for line in sys.stdin:  # line is formatted as foundword    foundwordcount
    line = line.strip()
    if line == '':
        continue

    # having this check here keeps us from loading this in every time we open an empty output file,
    # which tends to be quite frequently if we're dealing with pig output
    something_changed_in_file = True
    if not already_loaded_in_previous_file:
        already_loaded_in_previous_file = True

        searchword_count_dict = {}
        searchword_foundwords_dict = {}
        foundword_count_dict = {}

        if os.path.isfile(output_filename):
            # populate the three dicts with the information we've aggregated so far
            with open(output_filename, "r") as f:
                nonempty_files_so_far = f.readline().strip()
                this_is_output_file_num = 1 + int(nonempty_files_so_far[nonempty_files_so_far.index('from') + 5:
                                                                        nonempty_files_so_far.index('non-empty') - 1])
                for old_line in f:
                    old_line = old_line.rstrip()
                    if old_line == '':
                        continue
                    if not old_line.startswith('\t'):
                        searchword = old_line[:old_line.rfind(':')]
                        num_times_searchword_appeared = int(old_line[old_line.rfind(':') + 2:])
                        searchword_count_dict[searchword] = num_times_searchword_appeared
                        searchword_foundwords_dict[searchword] = []
                    else:
                        old_line = old_line.strip()
                        foundword = old_line[:old_line.rfind(':')]
                        searchword_foundwords_dict[searchword].append(foundword)
                        num_times_foundword_appeared = int(old_line[old_line.rfind(':') + 2:])
                        foundword_count_dict[foundword] = num_times_foundword_appeared
        else:
            this_is_output_file_num = 1

        print("Collecting information from nonempty file " + str(this_is_output_file_num) + " / " + total_num_files)

        keywords, strings_to_avoid_for_keyword = \
            get_keywords_and_keywords_strs_to_avoid("get_keyword_counts_keywords_to_count.txt")
        keyword_tuples = make_keyword_tuples(keywords, strings_to_avoid_for_keyword)
        keyword_tuples = [(kt[0][1:-1].replace('\\\\', '\\').replace('\\\'', '\''),
                           kt[1][1:-1].replace('\\\\', '\\').replace('\\\'', '\'').replace('\\[', '[')
                           .replace('\\^', '^').replace('\\$', '$').replace('\\.', '.').replace('\\|', '|')
                           .replace('\\?', '?').replace('\\*', '*').replace('\\+', '+').replace('\\(', '(')
                           .replace('\\)', ')'), kt)
                          for kt in keyword_tuples]

    match_inds = []
    match_keywords = []
    num_matches_within_foundwords = []
    foundword = line[:line.index('\t')]
    foundwordcount = int(line[line.index('\t') + 1:])
    for kt in keyword_tuples:
        # we don't need to use re.IGNORECASE flag, since everything will be lowercase already
        matches = [(m.start(0), m.end(0)) for m in re.finditer(kt[1], foundword)]
        if len(matches) > 0:
            error_message = ("WARNING: Matches are theoretically supposed to be mutually exclusive " +
                             "but we found some overlapping.\n")
            error_message += "\tIn " + foundword + ":\n"
            error_message += "\t" + str(match_keywords) + " and " + kt[0] + "\n"
            error_message += "\t" + str(match_inds)
            if not merge_match_lists(matches, match_inds):
                print(error_message)
            match_keywords.append(kt[0])
            num_matches_within_foundwords.append(len(matches))
    assert len(match_keywords) > 0, "No matches were found for a word that was flagged as a match"
    for i in range(len(match_keywords)):
        match = match_keywords[i]
        num_matches_within_foundword = num_matches_within_foundwords[i]
        try:
            searchword_count_dict[match] += foundwordcount
            searchword_foundwords_dict[match].append(foundword)
        except:
            searchword_count_dict[match] = foundwordcount
            searchword_foundwords_dict[match] = [foundword]
    try:
        foundword_count_dict[foundword] += foundwordcount
    except:
        foundword_count_dict[foundword] = foundwordcount

if something_changed_in_file:
    with open(output_filename, "w") as f:
        f.write("Aggregated results from " + str(this_is_output_file_num) + " non-empty output files\n")
        alphabetized_searchwords = []
        for key in searchword_count_dict.keys():
            alphabetized_searchwords.append(key)
        alphabetized_searchwords = sorted(alphabetized_searchwords)
        for searchword in alphabetized_searchwords:
            f.write(searchword + ": " + str(searchword_count_dict[searchword]) + '\n')
            alphabetized_foundwords = sorted(searchword_foundwords_dict[searchword])
            for foundword in alphabetized_foundwords:
                f.write('\t' + foundword + ": " + str(foundword_count_dict[foundword]) + '\n')
