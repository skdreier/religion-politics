from glob import glob
import sys
from tqdm import tqdm
from pull_out_all_religious_matches_with_local_context import get_list_of_distinct_religious_snippets_in_doc, \
    get_list_of_keywords_and_exceptions
from filter_contexts import get_inds_of_actual_matches_in_text

dir_name = sys.argv[1].strip()
if not dir_name.endswith('/'):
    dir_name += '/'


def get_ind_of_4th_tab_from_end(line):
    num_tabs_passed_so_far = 0
    for i in range(len(line) - 1, -1, -1):
        if line[i] == '\t':
            num_tabs_passed_so_far += 1
        if num_tabs_passed_so_far == 4:
            return i


dict_of_kw_to_except_before_after_strings = {}
# prepare keywords
previously_known_keywords_and_exceptions = get_list_of_keywords_and_exceptions('all_religious_words_postrnd1.txt')

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

if 'seminar' in dict_of_kw_to_except_before_after_strings:
    del dict_of_kw_to_except_before_after_strings['seminar']
    print('Removing "seminar" as keyword')
else:
    print('"seminar" was already not a keyword')


total_num_still_valid_snippets = 0
total_num_matches_to_decrease_by = 0
still_valid_doc_ids = {}
for fname in tqdm(list(glob(dir_name + '*'))):
    with open(fname, 'r') as f:
        for line in f:
            if len(line) < 2:
                continue
            words_included = line[:line.index('\t')]
            if words_included == 'seminar':
                line = line[line.index('\t') + 1:]
                num_matches = int(line[:line.index('\t')])
                total_num_matches_to_decrease_by += num_matches
                continue
            words_included = words_included.split(',')
            if 'seminar' in words_included:
                # make some decisions
                line = line[line.index('\t') + 1:]
                num_text_tab_ind = line.index('\t')
                original_num_matches = int(line[:num_text_tab_ind])
                line = line[num_text_tab_ind + 1:]
                text = line[:line.index('\t')]
                new_actual_match_inds = get_inds_of_actual_matches_in_text(text, words_included,
                                                                           dict_of_kw_to_except_before_after_strings,
                                                                           words_to_rem=['seminar'])
                assert len(new_actual_match_inds) < original_num_matches
                decreased_by_n_matches_in_this_snippet = original_num_matches - len(new_actual_match_inds)
                total_num_matches_to_decrease_by += decreased_by_n_matches_in_this_snippet
                if decreased_by_n_matches_in_this_snippet == original_num_matches:
                    continue
                else:
                    # see how many valid snippets there are left
                    new_snippets = get_list_of_distinct_religious_snippets_in_doc(text, 30,
                                                                   list_of_actual_matches=new_actual_match_inds)
                    total_num_still_valid_snippets += len(new_snippets)

                    # add doc_id to still-valid doc ids
                    line_id = line[get_ind_of_4th_tab_from_end(line) + 1:]
                    still_valid_doc_ids[line_id] = 0
            else:
                total_num_still_valid_snippets += 1
                line_id = line[get_ind_of_4th_tab_from_end(line) + 1:]
                still_valid_doc_ids[line_id] = 0


print('Total num matches TO SUBTRACT FROM PREV NUMBER: ' + str(total_num_matches_to_decrease_by))
print('Total num snippets that are still valid: ' + str(total_num_still_valid_snippets))
print('Total num page captures that are still valid: ' + str(len(still_valid_doc_ids)))
