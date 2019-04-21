from pull_out_all_religious_matches_with_local_context import get_list_of_keywords_and_exceptions, \
    make_regex, is_its_own_word
import re


keywords = get_list_of_keywords_and_exceptions('../all_religious_words.txt')
full_regex = '|'.join([make_regex(word_exceptions[0], word_exceptions[1]) for word_exceptions in keywords])


test_txt = 'here is a test containing the words "Seminary" and Seminar and we will hope only the first gets picked up.'


for match in re.finditer(full_regex, test_txt, flags=re.IGNORECASE):
    if is_its_own_word(test_txt, match.start(), match.end()):
        print(test_txt[match.start(): match.end()])
