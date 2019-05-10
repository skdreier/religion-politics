import sys
import os
import re
from glob import glob, iglob
from tqdm import tqdm
import multiprocessing
import datetime


context_window_size = 30  # number of words from either side of a religious match to pull
num_snippets_per_file = 50000
total_threads_to_use = 10
total_num_fnames_processed_per_thread = None
report_every_x_percent_of_files_done = 1


def get_list_of_keywords_and_exceptions(fname_of_keywords):
    with open(fname_of_keywords, "r") as f:
        keywords = []
        for line in f:
            if line.strip().startswith("#") or line.strip() == '':
                continue
            else:
                keyword = line.strip()
                keyword = list(re.split(r'(?<!\\)#', keyword))
                for j in range(len(keyword)):
                    actual_exception = ''
                    for letter in keyword[j]:
                        if letter != '\\':
                            actual_exception += letter
                    keyword[j] = actual_exception
                exceptions = [word.strip() for word in keyword[1:]]
                keyword = keyword[0].strip()
                keywords.append((keyword, exceptions))
    keywords = sorted(keywords, key=(lambda x: len(x[0])), reverse=True)
    return keywords


if __name__ == '__main__':
    filename_of_keywords = sys.argv[1]
    all_religious_docs_directory = sys.argv[2]
    output_religious_contexts_directory = sys.argv[3]
    if not all_religious_docs_directory.endswith('/'):
        all_religious_docs_directory += '/'
    if not output_religious_contexts_directory.endswith('/'):
        output_religious_contexts_directory += '/'
    if not os.path.isdir(output_religious_contexts_directory):
        os.makedirs(output_religious_contexts_directory)
    keywords = get_list_of_keywords_and_exceptions(filename_of_keywords)


def make_regex(inner_keyword, phrases_to_exclude):
    strings_not_to_match_before = []
    strings_not_to_match_after = []
    strings_not_to_match_before_and_after = []
    for i in range(len(phrases_to_exclude)):
        longer_keyword = phrases_to_exclude[i]
        while inner_keyword in longer_keyword:
            # figure out how to distinguish this shorter keyword from the longer keyword
            starting_ind_of_inner_keyword_in_larger = longer_keyword.index(inner_keyword)
            ending_ind_plus_1_of_inner_keyword_in_larger = starting_ind_of_inner_keyword_in_larger + len(inner_keyword)
            if starting_ind_of_inner_keyword_in_larger == 0:
                strings_not_to_match_after.append(longer_keyword[len(inner_keyword):])
            elif ending_ind_plus_1_of_inner_keyword_in_larger == len(longer_keyword):
                strings_not_to_match_before.append(longer_keyword[:longer_keyword.index(inner_keyword)])
            else:
                strings_not_to_match_before_and_after.append((longer_keyword[:starting_ind_of_inner_keyword_in_larger],
                                                              longer_keyword[starting_ind_of_inner_keyword_in_larger:]))
            longer_keyword = longer_keyword[starting_ind_of_inner_keyword_in_larger + len(inner_keyword):]

    regex = "(?:"
    for unmatch in strings_not_to_match_before_and_after:
        regex += "(?:(?<!"
        for letter in unmatch[0]:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += ")|"
        regex += "(?!"
        for letter in unmatch[1]:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += "))"

    for unmatch in strings_not_to_match_before:
        regex += "(?<!"
        for letter in unmatch:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += ")"

    # the keyword itself
    for letter in inner_keyword:
        if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                or letter == ')' or letter == "'"):
            regex += '\\'
        regex += letter

    for unmatch in strings_not_to_match_after:
        regex += "(?!"
        for letter in unmatch:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += ")"

    regex += ")"
    return regex


def is_its_own_word(doc, proposed_match_start, proposed_match_end_plus_1):
    if (proposed_match_start == 0 or not doc[proposed_match_start - 1].isalpha()) and \
            (proposed_match_end_plus_1 == len(doc) or not doc[proposed_match_end_plus_1].isalpha()):
        return True
    else:
        return False


def get_start_ind_of_next_word_to_left(doc, cur_ind):
    # assumes that next ind to left of cur_ind points to a space
    cur_ind -= 1
    while cur_ind > 0 and doc[cur_ind] == ' ':
        cur_ind -= 1
    if cur_ind == 0:
        return 0
    while cur_ind > 0 and doc[cur_ind] != ' ':
        cur_ind -= 1
    if doc[cur_ind] == ' ':
        return cur_ind + 1
    else:
        return cur_ind


def get_endp1_ind_of_next_word_to_right(doc, cur_ind):
    # assumes that next ind to right of cur_ind points to a space
    # cur_ind passed in as param should be end ind of word plus 1
    cur_ind += 1
    while cur_ind < len(doc) and doc[cur_ind - 1] == ' ':
        cur_ind += 1
    if cur_ind == len(doc):
        return len(doc)
    while cur_ind < len(doc) and doc[cur_ind - 1] != ' ':
        cur_ind += 1
    if doc[cur_ind - 1] == ' ':
        return cur_ind - 1
    else:
        return cur_ind


def get_start_ind_of_context(doc, start_ind_of_match, cws):
    num_complete_words_captured_so_far = 0
    cur_ind = start_ind_of_match
    if cur_ind == 0:
        return 0
    while cur_ind > 0 and num_complete_words_captured_so_far < cws:
        cur_ind = get_start_ind_of_next_word_to_left(doc, cur_ind)
        num_complete_words_captured_so_far += 1
    return cur_ind


def get_end_ind_plus_1_of_context(doc, end_ind_plus_1_of_match, cws, stop_if_gets_to=None):
    num_complete_words_captured_so_far = 0
    cur_ind = end_ind_plus_1_of_match
    if cur_ind == len(doc):
        return len(doc)
    while cur_ind < len(doc) and num_complete_words_captured_so_far <= cws:
        cur_ind = get_endp1_ind_of_next_word_to_right(doc, cur_ind)
        if stop_if_gets_to is not None and cur_ind >= stop_if_gets_to:
            return -1
        num_complete_words_captured_so_far += 1
    return cur_ind


def get_list_of_distinct_religious_snippets_in_doc(doc, cws, list_of_actual_matches=None,
                                                   include_num_matches_in_each_snippet=False):
    if list_of_actual_matches is None:
        list_of_actual_matches = []
        for match in re.finditer(full_regex, doc, flags=re.IGNORECASE):
            if is_its_own_word(doc, match.start(), match.end()):
                list_of_actual_matches.append((match.start(), match.end()))
    tups_of_matchkeywordlist_contextstart_contextendplus1 = []
    cur_start = None
    cur_num_matches_in_snippet = 0
    cur_list_of_religious_words_in_match = []
    for i in range(len(list_of_actual_matches)):
        if i < len(list_of_actual_matches) - 1:
            be_on_lookout_for_next_match_start = True
        else:
            be_on_lookout_for_next_match_start = False
        match_tup = list_of_actual_matches[i]
        keyword = doc[match_tup[0]: match_tup[1]]
        cur_num_matches_in_snippet += 1
        if keyword not in cur_list_of_religious_words_in_match:
            cur_list_of_religious_words_in_match.append(keyword)
        if cur_start is None:
            # we need to find the start of the context
            cur_start = get_start_ind_of_context(doc, match_tup[0], cws)
        if be_on_lookout_for_next_match_start:
            endp1ind_or_neg1ifoverlaps = get_end_ind_plus_1_of_context(doc, match_tup[1], cws,
                                                                       stop_if_gets_to=list_of_actual_matches[i + 1][0])
        else:
            endp1ind_or_neg1ifoverlaps = get_end_ind_plus_1_of_context(doc, match_tup[1], cws)
        if endp1ind_or_neg1ifoverlaps != -1:
            tups_of_matchkeywordlist_contextstart_contextendplus1.append((cur_list_of_religious_words_in_match,
                                                                          cur_start,
                                                                          endp1ind_or_neg1ifoverlaps,
                                                                          cur_num_matches_in_snippet))
            cur_start = None
            cur_num_matches_in_snippet = 0
            cur_list_of_religious_words_in_match = []
    if not include_num_matches_in_each_snippet:
        return [(','.join(tup[0]), doc[tup[1]: tup[2]]) for tup in
                tups_of_matchkeywordlist_contextstart_contextendplus1]
    else:
        return [(','.join(tup[0]), doc[tup[1]: tup[2]], tup[3]) for tup in
                tups_of_matchkeywordlist_contextstart_contextendplus1]


def get_tab_separated_fields(doc):
    doc_fields = doc.split('\t')
    url = doc_fields[0]
    surt = doc_fields[1]
    checksum = doc_fields[2]
    date = doc_fields[3]
    doc_text = doc_fields[-1]
    doc_text = doc_text.lower()
    return url, surt, checksum, date, doc_text


def get_chr1_separated_fields(doc):
    doc_fields = doc.split(chr(1))
    url = doc_fields[0]
    surt = doc_fields[1]
    checksum = doc_fields[2]
    date = doc_fields[3]
    doc_text = doc_fields[-1]
    doc_text = doc_text.lower()
    return url, surt, checksum, date, doc_text


def process_files_on_thread(list_of_files):
    if len(list_of_files) == 0:
        return
    thread_ind = list_of_files[0]
    end_of_thread_ind_str = thread_ind.rfind('.')
    if end_of_thread_ind_str < 0:
        end_of_thread_ind_str = len(thread_ind)
    thread_ind = int(thread_ind[thread_ind.rfind('-') + 1: end_of_thread_ind_str])

    num_snippets_in_cur_file = 0
    cur_file_starting_ind = 1
    cur_file_ending_ind_inclusive = num_snippets_per_file
    cur_open_file = open(output_religious_contexts_directory + str(thread_ind) + '_'+ str(cur_file_starting_ind) +
                         '-' + str(cur_file_ending_ind_inclusive) + '.txt', 'w')
    step_size = total_num_fnames_processed_per_thread / (100 / report_every_x_percent_of_files_done)
    next_marker = step_size
    for file_ind in range(len(list_of_files)):
        doc_fname = list_of_files[file_ind]
        with open(doc_fname, 'r') as f:
            for doc_line in f:
                doc = doc_line.strip()
                if doc == '':
                    continue
                url, surt, checksum, date, doc_text = get_chr1_separated_fields(doc)  # get_tab_separated_fields(doc)

                matchwords_matchsnippets_nummatches = \
                    get_list_of_distinct_religious_snippets_in_doc(doc_text, context_window_size,
                                                                   include_num_matches_in_each_snippet=True)

                for match_tup in matchwords_matchsnippets_nummatches:
                    cur_open_file.write('\t'.join([match_tup[0], str(match_tup[2]), match_tup[1],
                                                   url, surt, checksum, date]) + '\n')
                    num_snippets_in_cur_file += 1
                    if num_snippets_in_cur_file == num_snippets_per_file:
                        cur_open_file.close()
                        cur_file_starting_ind += num_snippets_per_file
                        cur_file_ending_ind_inclusive += num_snippets_per_file
                        cur_open_file = open(output_religious_contexts_directory + str(thread_ind) + '_'+
                                             str(cur_file_starting_ind) + '-' + str(cur_file_ending_ind_inclusive) +
                                             '.txt', 'w')
                        num_snippets_in_cur_file = 0
        #print("Done processing " + doc_fname + " at " + str(datetime.datetime.now()))
        if file_ind + 1 >= next_marker:
            print(str(int(100 * next_marker / total_num_fnames_processed_per_thread)) +
                  '% done with files on thread ' + str(thread_ind) + ' at ' + str(datetime.datetime.now()))
            next_marker += step_size

    # now rename last file to be accurate about its end ind
    cur_open_file.close()
    last_file_name = (output_religious_contexts_directory + str(thread_ind) + '_'+ str(cur_file_starting_ind) +
                      '-' + str(cur_file_ending_ind_inclusive) + '.txt')
    if num_snippets_in_cur_file == 0:
        os.remove(last_file_name)
    elif num_snippets_in_cur_file != num_snippets_per_file:
        cur_file_ending_ind_inclusive = cur_file_starting_ind + num_snippets_in_cur_file - 1
        new_file_name = (output_religious_contexts_directory + str(thread_ind) + '_'+ str(cur_file_starting_ind) +
                         '-' + str(cur_file_ending_ind_inclusive) + '.txt')
        os.rename(last_file_name, new_file_name)

    print("Success on thread " + str(thread_ind) + ".")


def try_pool(num_threads):
    #all_doc_filenames = sorted(list(glob(all_religious_docs_directory + '*')))
    all_doc_filenames = sorted(list(iglob(all_religious_docs_directory + '**/part-*', recursive=True)))
    global total_num_fnames_processed_per_thread
    total_num_fnames_processed_per_thread = len(all_doc_filenames) / num_threads

    lists_of_filenames = []
    for i in range(num_threads):
        lists_of_filenames.append([])
    for i in range(len(all_doc_filenames)):
        lists_of_filenames[i % num_threads].append(all_doc_filenames[i])
    for list_of_filenames in lists_of_filenames:
        initial_len_list = len(list_of_filenames)
        list_of_filenames.reverse()  # big files first to help estimate worst-case scenario for time
        list_of_filenames.insert(0, list_of_filenames[-1])
        assert list_of_filenames[0] == list_of_filenames[-1]
        del list_of_filenames[-1]
        assert initial_len_list == len(list_of_filenames)
    try:
        print("Total num doc filenames: " + str(len(all_doc_filenames)) + " (" + str(datetime.datetime.now()) + ")")
        pool = multiprocessing.Pool(processes=num_threads)
        list_of_wordcount_dicts = pool.map(process_files_on_thread, lists_of_filenames)
    except Exception as e:

        pool.close()
        print("Issue with pool: ")
        print(e)
        return False
    pool.close()
    return list_of_wordcount_dicts


if __name__ == '__main__':
    full_regex = '|'.join([make_regex(word_exceptions[0], word_exceptions[1]) for word_exceptions in keywords])
    try_pool(total_threads_to_use)
    print("Done.")
