import re
from pull_out_all_religious_matches_with_local_context import make_regex, get_list_of_keywords_and_exceptions, \
         get_list_of_distinct_religious_snippets_in_doc
from filter_contexts import get_inds_of_actual_matches_in_text
from filter_contexts import get_inds_of_actual_matches_in_text


text_to_check = ("or discussion. the taliban must act and act immediately. they will hand " +
                 "over the terrorists or they will share in their fate. i also want to speak " +
                 "tonight directly to muslims throughout the world. we respect your faith. " +
                 "it's practiced freely by many millions of americans and by millions more in " +
                 "countries that america counts as friends. its teachings are good and peaceful, " +
                 "and those who commit evil in the name of allah blaspheme the name of allah. " +
                 "the terrorists are traitors to their own faith, trying, in effect, to hijack " +
                 "islam itself. the enemy of america is not our many muslim friends. it is not " +
                 "our many arab friends. our enemy is a radical network of terrorists and every " +
                 "government that supports them. our war on terror begins with al qaeda")


filename_of_keywords = '../modified_order_religious_words.txt'
keywords = get_list_of_keywords_and_exceptions(filename_of_keywords)
full_regex = '|'.join([make_regex(word_exceptions[0], word_exceptions[1]) for word_exceptions in keywords])
print(full_regex)
full_regex = re.compile(full_regex)


list_of_actual_matches = get_inds_of_actual_matches_in_text(text_to_check,
                                                            ['evil', 'allah', 'faith','islam','muslims', 'muslim'],
                                                            {'evil':[], 'allah':[], 'faith':[],'islam':[],'muslims':[], 'muslim':[]},
                                                            words_to_rem={})
matchwords_matchsnippets = get_list_of_distinct_religious_snippets_in_doc(text_to_check, 30,
                                                                          list_of_actual_matches=list_of_actual_matches,
                                                                          include_num_matches_in_each_snippet=True)
for item in matchwords_matchsnippets:
    print(item)

print()
word_list = ['evil','allah','faith','islam','muslim', 'muslims']
exceptions = {'evil':[],'allah':[],'faith':[('good ', '')],'islam':[],'muslim':[], 'muslims':[]}
list_of_inds = get_inds_of_actual_matches_in_text(text_to_check, word_list, exceptions)
text_to_print = ''
next_text_collecting_ind = 0
for match_tup in list_of_inds:
    text_to_print += text_to_check[next_text_collecting_ind: max([0, match_tup[0]])]
    text_to_print += text_to_check[match_tup[0]: match_tup[1]].upper()
    next_text_collecting_ind = match_tup[1]
text_to_print += text_to_check[next_text_collecting_ind:]
print(text_to_print)
print(str(len(list_of_inds)) + ' matches found.')


from merge_snippets_that_should_have_been_together import process_filename
process_filename('test_file.txt', 'temp.txt', exceptions)


filename_of_keywords = '../all_religious_words.txt'
keywords = get_list_of_keywords_and_exceptions(filename_of_keywords)

from filter_contexts import write_modified_version_of_file_to_temp_file, pare_down_new_wordstorem_and_exceptions_based_on_old_ones

# prepare keywords
words_to_remove = {}
with open('../keywords_to_discard.txt', 'r') as f:
    for line in f:
        word = line.strip().lower()
        if word == '':
            continue
        words_to_remove[word] = 0
words_to_new_exceptions = {}
with open('../keywords_with_new_exceptions.txt', 'r') as f:
    for line in f:
        line = line.strip().lower()
        if line == '':
            continue
        line = [item.strip() for item in line.split('#')]
        words_to_new_exceptions[line[0]] = line[1:]

previously_known_keywords_and_exceptions = get_list_of_keywords_and_exceptions(filename_of_keywords)
words_to_remove, words_to_new_exceptions = \
    pare_down_new_wordstorem_and_exceptions_based_on_old_ones(previously_known_keywords_and_exceptions,
                                                              words_to_remove, words_to_new_exceptions)

dict_of_old_kw_to_old_exceptions = {}
for kw_tup in previously_known_keywords_and_exceptions:
    dict_of_old_kw_to_old_exceptions[kw_tup[0]] = kw_tup[1]

full_exceptions_dict = {}
for kw in dict_of_old_kw_to_old_exceptions:
    if kw in words_to_new_exceptions:
        full_exceptions_dict[kw] = dict_of_old_kw_to_old_exceptions[kw] + words_to_new_exceptions[kw]
    else:
        full_exceptions_dict[kw] = dict_of_old_kw_to_old_exceptions[kw]
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

write_modified_version_of_file_to_temp_file('original_2.txt', 'temp2.txt', )