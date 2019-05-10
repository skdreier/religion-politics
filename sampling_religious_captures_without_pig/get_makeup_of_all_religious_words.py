from glob import glob
import sys
from tqdm import tqdm
from pull_out_all_religious_matches_with_local_context import get_list_of_keywords_and_exceptions
from filter_contexts import get_inds_of_actual_matches_in_text

dir_name = sys.argv[1].strip()
keyword_filename = sys.argv[2].strip()
if not dir_name.endswith('/'):
    results_filename = dir_name + '-makeupresults.txt'
    dir_name += '/'
else:
    results_filename = dir_name[:-1] + '-makeupresults.txt'


keywords_and_exceptions = get_list_of_keywords_and_exceptions(keyword_filename)
dict_of_kw_to_exceptions = {}
for kw_tup in keywords_and_exceptions:
    dict_of_kw_to_exceptions[kw_tup[0]] = kw_tup[1]
dict_of_kw_to_except_before_after_strings = {}
for keyword_match in dict_of_kw_to_exceptions:
    possible_exceptions = dict_of_kw_to_exceptions[keyword_match]
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


words_to_counts = {}
for fname in tqdm(list(glob(dir_name + '*'))):
    with open(fname, 'r') as f:
        for line in f:
            if len(line) < 2:
                continue
            line_pieces = line.split('\t')
            num_matches = int(line_pieces[1])
            keywords = line_pieces[0].split(',')
            text = line_pieces[2]
            list_of_actual_matches = get_inds_of_actual_matches_in_text(text, keywords,
                                                                        dict_of_kw_to_except_before_after_strings)

            if len(list_of_actual_matches) > num_matches:
                assert len(list_of_actual_matches) == num_matches + 1
                # look for whether the religious word to cut off (assume it's only one) happens at either the
                # very beginning or the very end
                if list_of_actual_matches[0][0] < 15:
                    is_first_match = True
                else:
                    is_first_match = False
                if list_of_actual_matches[-1][1] > len(text) - 15:
                    is_last_match = True
                else:
                    is_last_match = False

                assert (is_first_match or is_last_match and (not (is_first_match and is_last_match)))
                if is_first_match:
                    # cut off the first match
                    list_of_actual_matches = list_of_actual_matches[1:]
                elif is_last_match:
                    list_of_actual_matches = list_of_actual_matches[:-1]
            assert len(list_of_actual_matches) == num_matches

            for match in list_of_actual_matches:
                match_word = text[match[0]: match[1]]
                if match_word in words_to_counts:
                    words_to_counts[match_word] += 1
                else:
                    words_to_counts[match_word] = 1


# now write results to file
total_num_matches = sum(list(words_to_counts.values()))
with open(results_filename, 'w') as f:
    for word in sorted(list(words_to_counts.keys())):
        f.write(word + ': \t')
        pct_of_all_religious_words = 100 * words_to_counts[word] / total_num_matches
        f.write(str(pct_of_all_religious_words) + '% of all matches (raw count: ' + str(words_to_counts[word]) + ')\n')
print('Done writing results to ' + results_filename)
