from filter_contexts import get_inds_of_actual_matches_in_text
from pull_out_all_religious_matches_with_local_context import get_list_of_keywords_and_exceptions
from tqdm import tqdm
from glob import glob
import shutil
import os


full_keyword_file = 'all_religious_words.txt'
original_dir = 'all_religious_word_contexts/'
new_dir = 'all_religious_word_contexts_gapfixed/'
if not os.path.isdir(new_dir):
    os.makedirs(new_dir)


def get_num_words_after():
    return 0


def get_index_of_fourth_tab_from_end(text):
    num_tabs_so_far = 0
    for i in range(len(text) - 1, -1, -1):
        if text[i] == '\t':
            num_tabs_so_far += 1
            if num_tabs_so_far == 4:
                return i


def get_words_num_text_out_of_string(words_num_text):
    first_tab_ind = words_num_text.index('\t')
    words = words_num_text[:first_tab_ind].split(',')
    words_num_text = words_num_text[first_tab_ind + 1:]
    next_tab_ind = words_num_text.index('\t')
    num = int(words_num_text[:next_tab_ind])
    text = words_num_text[next_tab_ind + 1:]
    return words, num, text


def string_at_ind_starts_with_actual_match(text, list_of_terms, starting_ind):
    next_inds_of_words_looking_for = [0] * len(list_of_terms)
    for i in range(starting_ind, len(text)):
        cur_char = text[i]
        for j in range(len(list_of_terms)):
            if next_inds_of_words_looking_for[j] == 0:
                if cur_char == list_of_terms[j][0] and (i == 0 or not text[i - 1].isalpha()):
                    next_inds_of_words_looking_for[j] += 1
            elif next_inds_of_words_looking_for[j] < len(list_of_terms[j]):
                if cur_char == list_of_terms[j][next_inds_of_words_looking_for[j]]:
                    next_inds_of_words_looking_for[j] += 1
                else:
                    next_inds_of_words_looking_for[j] = 0  # wasn't actually a match
            else:  # if next_inds_of_words_looking_for[j] == len(list_of_terms[j]):
                if not cur_char.isalpha():
                    # it's a match!
                    return True, (i - len(list_of_terms[j]), i)
                else:
                    next_inds_of_words_looking_for[j] = 0  # wasn't actually a match
        if sum(next_inds_of_words_looking_for) == 0:
            return False, None

    for j in range(len(list_of_terms)):
        if next_inds_of_words_looking_for[j] == len(list_of_terms[j]):
            # it's a match!
            return True, (len(text) - len(list_of_terms[j]), len(text))
    return False, None


def get_starting_ind_of_last_religious_match_in_text(text, list_of_terms):
    next_inds_of_words_looking_for = [len(word) - 1 for word in list_of_terms]
    for i in range(len(text) - 1, -1, -1):
        cur_char = text[i]
        for j in range(len(list_of_terms)):
            if next_inds_of_words_looking_for[j] == len(list_of_terms[j]) - 1:
                if cur_char == list_of_terms[j][-1] and (i == len(text) - 1 or not text[i + 1].isalpha()):
                    next_inds_of_words_looking_for[j] -= 1
            elif next_inds_of_words_looking_for[j] >= 0:
                if cur_char == list_of_terms[j][next_inds_of_words_looking_for[j]]:
                    next_inds_of_words_looking_for[j] -= 1
                else:
                    next_inds_of_words_looking_for[j] = len(list_of_terms[j]) - 1  # wasn't actually a match
            else:  # if next_inds_of_words_looking_for[j] == len(list_of_terms[j]):
                if not cur_char.isalpha():
                    return i + 1  # we found our first match!
                else:
                    next_inds_of_words_looking_for[j] = len(list_of_terms[j]) - 1  # wasn't actually a match

    for j in range(len(list_of_terms)):
        if next_inds_of_words_looking_for[j] == -1:
            return 0

    return None


def check_whether_should_be_merged(old_words_num_text, new_words_num_text, kws_to_except_before_after):
    # separate out the three fields
    new_words, new_num, new_text = get_words_num_text_out_of_string(new_words_num_text)

    # check text in new string until you reach first alpha character: is that the start of a match?
    cur_ind = 0
    while cur_ind < len(new_text) - 1 and not new_text[cur_ind].isalpha():
        cur_ind += 1
    if cur_ind < len(new_text) and new_text[cur_ind].isalpha():
        # check whether this is a keyword match
        is_kw_match, kw_match_inds = string_at_ind_starts_with_actual_match(new_text, new_words, cur_ind)
        if not is_kw_match:
            return False, None
        else:
            new_text_modified = new_text[kw_match_inds[0]:]
            num_chars_cut_off = len(new_text) - len(new_text_modified)
            new_text = new_text_modified
            kw_match_inds = [kw_match_inds[0] - num_chars_cut_off, kw_match_inds[1] - num_chars_cut_off]
            assert kw_match_inds[0] == 0
    else:
        return False, None

    # beginning of the new passage should be the end of the old one, stretching from the start of the
    # last religious match to the end
    old_words, old_num, old_text = get_words_num_text_out_of_string(old_words_num_text)
    starting_ind_of_last_match = get_starting_ind_of_last_religious_match_in_text(old_text, old_words)
    if not new_text.startswith(old_text[starting_ind_of_last_match:]):
        return False, None

    # should be just non-alpha characters from the end of that overlap to the start of the 2nd
    # religious match logged in the follow-up
    num_chars_in_already_checked_overlap = len(old_text) - starting_ind_of_last_match
    assert len(old_text[starting_ind_of_last_match:]) == num_chars_in_already_checked_overlap
    assert len(new_text) >= num_chars_in_already_checked_overlap, str(len(new_text)) + ", " + \
                                                                  str(num_chars_in_already_checked_overlap)
    cur_ind = num_chars_in_already_checked_overlap
    while cur_ind < len(new_text) - 1 and not new_text[cur_ind].isalpha():
        cur_ind += 1
    if cur_ind < len(new_text) and new_text[cur_ind].isalpha():
        next_block_is_kw_match, _ = string_at_ind_starts_with_actual_match(new_text, new_words, cur_ind)
        if next_block_is_kw_match:
            # these blocks should be merged. Return a) union of kws b) num + num - 1 c) merged text as string
            union_of_kws = list(set(old_words) | set(new_words))
            text_to_return = old_text[:starting_ind_of_last_match] + new_text
            new_num_matches = len(get_inds_of_actual_matches_in_text(text_to_return, union_of_kws,
                                                                     kws_to_except_before_after))
            return True, ','.join(union_of_kws) + '\t' + str(new_num_matches) + '\t' + text_to_return
        else:
            return False, None
    else:
        return False, None


def process_filename(filename, new_filename, kws_to_except_before_after):
    prev_line_tag = ''
    prev_line_words_num_text = ''
    new_f = open(new_filename, 'w')
    num_snippets_included = 0
    original_num_snippets = 0
    with open(filename, 'r') as f:
        for line in f:
            if len(line) <= 2:
                continue
            original_num_snippets += 1
            ind_of_tab_separating_tag_from_text = get_index_of_fourth_tab_from_end(line)
            new_line_tag = line[ind_of_tab_separating_tag_from_text:]
            new_line_words_num_text = line[:ind_of_tab_separating_tag_from_text]

            # if prev's tag doesn't match this one's, write prev line as a match
            if prev_line_tag != new_line_tag:
                # record previous line
                new_f.write(prev_line_words_num_text + prev_line_tag)
                num_snippets_included += 1
                prev_line_words_num_text = new_line_words_num_text
                prev_line_tag = new_line_tag
            else:
                is_combined_match, combined_words_num_text = \
                    check_whether_should_be_merged(prev_line_words_num_text, new_line_words_num_text,
                                                   kws_to_except_before_after)
                if is_combined_match:
                    prev_line_words_num_text = combined_words_num_text
                else:
                    new_f.write(prev_line_words_num_text + prev_line_tag)
                    num_snippets_included += 1
                    prev_line_words_num_text = new_line_words_num_text
                    prev_line_tag = new_line_tag

    if len(prev_line_tag) > 1:
        new_f.write(prev_line_words_num_text + prev_line_tag)
        num_snippets_included += 1
    new_f.close()
    return num_snippets_included, original_num_snippets


def reprocess_files(old_dir, new_dir, kws_to_except_before_after):
    # modify files
    cur_thread_ind = 0
    temp_filename = new_dir + 'temp.txt'
    total_num_snippets_so_far = 0
    original_num_snippets = 0
    pbar = tqdm(desc='Updating files', total=len(list(glob(old_dir + '*'))))
    while len(list(glob(old_dir + str(cur_thread_ind) + '_1-*'))) > 0:
        num_snippets_included_so_far = 0
        prev_snippets_iterated_through = 0
        first_fname_list = list(glob(old_dir + str(cur_thread_ind) + '_1-*'))
        assert len(first_fname_list) == 1
        cur_fname_list = first_fname_list
        while len(cur_fname_list) > 0:
            assert len(cur_fname_list) == 1
            cur_fname = cur_fname_list[0]

            new_snippets_included, num_snippets_in_original_file = process_filename(cur_fname, temp_filename,
                                                                                    kws_to_except_before_after)
            original_num_snippets += num_snippets_in_original_file

            starting_snippet_of_file = num_snippets_included_so_far + 1
            num_snippets_included_so_far += new_snippets_included
            prev_snippets_iterated_through += num_snippets_in_original_file
            new_filename = (new_dir + str(cur_thread_ind) + '_' + str(starting_snippet_of_file) + '-' +
                            str(num_snippets_included_so_far) + '.txt')
            shutil.move(temp_filename, new_filename)

            cur_fname_list = list(glob(old_dir + str(cur_thread_ind) + '_' +
                                       str(prev_snippets_iterated_through + 1) + '-*'))
            pbar.update(1)
        cur_thread_ind += 1
        total_num_snippets_so_far += num_snippets_included_so_far
    pbar.close()
    print("Condensed down to " + str(total_num_snippets_so_far) + " snippets out of an original " +
          str(original_num_snippets) + ".")


def main():
    keywords_and_exceptions = get_list_of_keywords_and_exceptions(full_keyword_file)
    full_exceptions_dict = {}
    for kw in keywords_and_exceptions:
        full_exceptions_dict[kw[0]] = kw[1]
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
    reprocess_files(original_dir, new_dir, dict_of_kw_to_except_before_after_strings)


if __name__ == '__main__':
    main()
