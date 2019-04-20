# collect all unique logged keywords
# add counts of occurrences, not just number of snippets

from filter_contexts import get_inds_of_actual_matches_in_text
from pull_out_all_religious_matches_with_local_context import get_list_of_keywords_and_exceptions
from glob import glob
import os
from tqdm import tqdm


dir_to_add_counts_to = 'all_religious_word_contexts/'
if not dir_to_add_counts_to.endswith('/'):
    dir_to_add_counts_to += '/'


previously_known_keywords_and_exceptions = get_list_of_keywords_and_exceptions('all_religious_words.txt')
full_exceptions_dict = {}
for kw_tup in previously_known_keywords_and_exceptions:
    full_exceptions_dict[kw_tup[0]] = kw_tup[1]
dict_of_kw_to_except_before_after_strings = {}
for keyword_match in full_exceptions_dict:
    possible_exceptions = full_exceptions_dict[keyword_match]
    before_and_after_pairs_to_look_out_for = []
    for exception in possible_exceptions:
        all_starting_inds_of_kw_in_exception = []
        remaining_string = exception
        while remaining_string.rfind(keyword_match) != -1:
            start_ind = remaining_string.rfind(keyword_match)
            all_starting_inds_of_kw_in_exception.append(start_ind)
            remaining_string = remaining_string[: start_ind + len(keyword_match) - 1]
        for start_ind in all_starting_inds_of_kw_in_exception:
            before_and_after_pairs_to_look_out_for.append((exception[:start_ind],
                                                           exception[start_ind + len(keyword_match):]))
    dict_of_kw_to_except_before_after_strings[keyword_match] = before_and_after_pairs_to_look_out_for


temp_filename = dir_to_add_counts_to + 'temp.txt'
all_keywords_appearing = {}
for filename in tqdm(glob(dir_to_add_counts_to + '*')):
    if not os.path.isfile(filename):
        continue
    new_f = open(temp_filename, 'w')
    is_actual_file_needing_processing = True
    num_lines_written_so_far = 0
    with open(filename, 'r') as f:
        for line in f:
            first_tab_ind = line.index('\t')
            keyword_block = line[:first_tab_ind]
            keyword_list = keyword_block.split(',')
            for keyword in keyword_list:
                if keyword not in all_keywords_appearing:
                    all_keywords_appearing[keyword] = 0
            part_of_line_starting_with_text = line[first_tab_ind + 1:]
            ind_of_first_tab_after_text = part_of_line_starting_with_text.index('\t')
            text = part_of_line_starting_with_text[:ind_of_first_tab_after_text]
            rest_of_line = part_of_line_starting_with_text[ind_of_first_tab_after_text:]

            match_inds = get_inds_of_actual_matches_in_text(text, keyword_list,
                                                            dict_of_kw_to_except_before_after_strings)
            if not is_actual_file_needing_processing:
                try:
                    int(text)
                except:
                    assert False, '\n' + text + '\n' + keyword_block + '\n' + \
                                  str([text[kw[0]: kw[1]] for kw in match_inds])
            num_matches = len(match_inds)
            is_actual_file_needing_processing = (num_matches >= len(keyword_list))
            if is_actual_file_needing_processing:
                new_f.write(keyword_block + '\t' + str(num_matches) + '\t' + text + rest_of_line)
                num_lines_written_so_far += 1
            else:
                assert num_lines_written_so_far == 0, '\n' + text + '\n' + keyword_block + '\n' + \
                                                      str([text[kw[0]: kw[1]] for kw in match_inds])
    new_f.close()
    if is_actual_file_needing_processing:
        os.rename(temp_filename, filename)
    else:
        os.remove(temp_filename)


with open("all_logged_keywords.txt", 'w') as f:
    for kw in sorted(list(all_keywords_appearing.keys())):
        f.write(kw + '\n')
