from glob import glob
from tqdm import tqdm
import numpy as np
from pull_out_all_religious_matches_with_local_context import get_start_ind_of_context, get_end_ind_plus_1_of_context, \
    get_list_of_keywords_and_exceptions
from filter_contexts import get_inds_of_actual_matches_in_text


how_many_to_sample = 200
num_chars_around_match_to_pull = 50
num_words_around_match_to_pull = 10  # deprecated
output_filename = 'sampled_religious_word_contexts_4-22.txt'
dir_of_all_matches = 'all_religious_word_contexts_gapfixed/'
keyword_file = 'all_religious_words.txt'


if not dir_of_all_matches.endswith('/'):
    dir_of_all_matches += '/'
filenames = sorted(list(glob(dir_of_all_matches + '*')))


total_num_matches = 0
for fname in tqdm(filenames, desc='Counting how many rel word matches there are in total'):
    with open(fname, 'r') as f:
        for line in f:
            line = line[line.index('\t') + 1:]
            line = int(line[:line.index('\t')])
            total_num_matches += line

print("Found " + str(total_num_matches) + " religious matches in total.")


def get_shortened_context_for_ith_relmatchword_in_snippet(snippet, keyword, index_of_keyword,
                                                          num_words_around_match_to_pull):
    assert keyword == snippet[index_of_keyword: index_of_keyword + len(keyword)], \
      keyword + '\n' + snippet + '\n' + snippet[index_of_keyword: index_of_keyword + len(keyword)]

    start_ind = get_start_ind_of_context(snippet, index_of_keyword, num_words_around_match_to_pull)
    end_ind_p1 = get_end_ind_plus_1_of_context(snippet, index_of_keyword + len(keyword),
                                               num_words_around_match_to_pull)
    return snippet[start_ind: end_ind_p1]


previously_known_keywords_and_exceptions = get_list_of_keywords_and_exceptions(keyword_file)
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


inds_to_pull = np.sort(np.random.choice(total_num_matches, size=how_many_to_sample, replace=False))
cur_ind_ind = 0
matches_passed_so_far = 0
words_to_contexts = {}
done = False
for fname in tqdm(filenames, desc='Pulling out sampled matches'):
    if done:
        break
    with open(fname, 'r') as f:
        for line in f:
            if done:
                break
            num_matches_in_line = line[line.index('\t') + 1:]
            num_matches_in_line = int(num_matches_in_line[:num_matches_in_line.index('\t')])
            if inds_to_pull[cur_ind_ind] > matches_passed_so_far + num_matches_in_line - 1:
                matches_passed_so_far += num_matches_in_line
                continue
            line = line.split('\t')
            doc = line[2]
            keyword_list = line[0].split(',')
            match_ind_list = get_inds_of_actual_matches_in_text(doc, keyword_list,
                                                                dict_of_kw_to_except_before_after_strings)
            for i in range(len(match_ind_list)):
                if matches_passed_so_far == inds_to_pull[cur_ind_ind]:
                    keyword = doc[match_ind_list[i][0]: match_ind_list[i][1]]
                    context = doc[max([0, match_ind_list[i][0] - num_chars_around_match_to_pull]):
                                  match_ind_list[i][1] + num_chars_around_match_to_pull]
                    assert keyword in context, '\n' + keyword + '\n' + context + '\n' + str(match_ind_list[i]) \
                        + '\n' + doc
                    if keyword in words_to_contexts:
                        words_to_contexts[keyword].append(context)
                    else:
                        words_to_contexts[keyword] = [context]
                    cur_ind_ind += 1
                    if cur_ind_ind == inds_to_pull.shape[0]:
                        done = True
                        break
                matches_passed_so_far += 1


with open(output_filename, 'w') as f:
    for word in sorted(list(words_to_contexts.keys())):
        f.write(word + ':\n')
        for context in words_to_contexts[word]:
            f.write('\t' + context + '\n')
        f.write('\n')


print("Done.")
