# go through files, look for words with changes, and adjust their counts accordingly

import os
from glob import glob
from tqdm import tqdm
from pull_out_all_religious_matches_with_local_context import make_regex, get_list_of_keywords_and_exceptions, \
    get_list_of_distinct_religious_snippets_in_doc, context_window_size


filename_of_words_to_remove_entirely = 'keywords_to_discard.txt'
filename_of_words_with_new_exceptions = 'keywords_with_new_exceptions.txt'

full_keyword_file_to_edit_later = 'all_religious_words.txt'
dir_to_modify = 'all_religious_word_contexts/'


if __name__ == '__main__':
    # read in args
    if not dir_to_modify.endswith('/'):
        dir_to_modify += '/'
    keyword_list_field = 0
    keyword_count_field = 1
    text_field = 2
    assert keyword_list_field == 0, "Code counts on this"


# double-check that all of these are actually new when compared against contents of full keyword file
def pare_down_new_wordstorem_and_exceptions_based_on_old_ones(prev_known_keywords_and_exceptions,
                                                              words_to_rem, words_to_new_except):
    keys_to_remove = []
    for word in words_to_rem:
        appeared_as_keyword_before = False
        for word_tup in prev_known_keywords_and_exceptions:
            if word_tup[0] == word:
                appeared_as_keyword_before = True
                break
        if not appeared_as_keyword_before:
            print(word + " didn't appear as keyword before, so there won't be any flagged examples of it.")
            keys_to_remove.append(word)
    for word in keys_to_remove:
        del words_to_rem[word]

    keys_to_remove = []
    for word in words_to_new_except:
        exceptions_not_known_before = []
        draft_list_of_exceptions = words_to_new_except[word]
        for word_tup in prev_known_keywords_and_exceptions:
            if word_tup[0] == word:
                previously_known_exceptions = word_tup[1]
                for new_potential_exception in draft_list_of_exceptions:
                    if new_potential_exception not in previously_known_exceptions:
                        exceptions_not_known_before.append(new_potential_exception)
                    else:
                        print("For keyword " + word_tup[0] + ", " + new_potential_exception +
                              " was already listed as an exception.")
        words_to_new_except[word] = exceptions_not_known_before
        if len(exceptions_not_known_before) == 0:
            keys_to_remove.append(word)
    for word in keys_to_remove:
        del words_to_new_except[word]
    return words_to_rem, words_to_new_except


def get_inds_of_exact_matches_to_short_list_of_terms(text, list_of_terms):
    complete_matches = []
    next_inds_of_words_looking_for = [0] * len(list_of_terms)
    for i in range(len(text)):
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
                    complete_matches.append((i - len(list_of_terms[j]), i))
                    next_inds_of_words_looking_for[j] = 0
                else:
                    next_inds_of_words_looking_for[j] = 0  # wasn't actually a match

    for j in range(len(list_of_terms)):
        if next_inds_of_words_looking_for[j] == len(list_of_terms[j]):
            complete_matches.append((len(text) - len(list_of_terms[j]), len(text)))
    return complete_matches


def get_inds_of_actual_matches_in_text(text, keyword_list, dict_of_kw_to_except_before_after_strings,
                                       words_to_rem=None):
    all_surface_level_matches = get_inds_of_exact_matches_to_short_list_of_terms(text, keyword_list)
    for i in range(len(all_surface_level_matches) - 1, -1, -1):
        match_inds = all_surface_level_matches[i]
        keyword_match = text[match_inds[0]: match_inds[1]]
        if words_to_rem is not None and keyword_match in words_to_rem:
            del all_surface_level_matches[i]
        elif len(dict_of_kw_to_except_before_after_strings[keyword_match]) > 0:
            # this might be an exception: check for that
            part_before_word = text[:match_inds[0]]
            part_after_word = text[match_inds[1]:]
            full_exceptions_for_kw = dict_of_kw_to_except_before_after_strings[keyword_match]
            for exception_tup in full_exceptions_for_kw:
                first_part = exception_tup[0]
                second_part = exception_tup[1]
                if first_part != '' and second_part != '':
                    part_before_word_ends_with_first_part = ((part_before_word.rfind(first_part) != -1) and
                                                             (part_before_word.rfind(first_part) ==
                                                             len(part_before_word) - len(first_part)))
                    part_after_word_starts_with_second_part = False
                    try:
                        ind = part_after_word.index(second_part)
                        if ind == 0:
                            part_after_word_starts_with_second_part = True
                    except:
                        pass
                    if part_before_word_ends_with_first_part and part_after_word_starts_with_second_part:
                        # this is definitely an exception -- remove it as a match
                        del all_surface_level_matches[i]
                        break
                elif first_part != '':
                    part_before_word_ends_with_first_part = ((part_before_word.rfind(first_part) != -1) and
                                                             (part_before_word.rfind(first_part) ==
                                                             len(part_before_word) - len(first_part)))
                    if part_before_word_ends_with_first_part:
                        # this is definitely an exception -- remove it as a match
                        del all_surface_level_matches[i]
                        break
                elif second_part != '':
                    part_after_word_starts_with_second_part = False
                    try:
                        ind = part_after_word.index(second_part)
                        if ind == 0:
                            part_after_word_starts_with_second_part = True
                    except:
                        pass
                    if part_after_word_starts_with_second_part:
                        # this is definitely an exception -- remove it as a match
                        del all_surface_level_matches[i]
                        break
                else:
                    assert False, "First and second part of an exception should never both be blank: \n" + \
                                  "Keyword: " + keyword_match + '\nFirst part: (' + first_part + \
                                  ')\nSecond part: (' + second_part + ')'
    return all_surface_level_matches


def assemble_new_line_given_new_parts_and_prev_line_bits(old_fields, new_kw_block, new_text, new_num_matches):
    old_fields[keyword_list_field] = new_kw_block
    old_fields[keyword_count_field] = str(new_num_matches)
    old_fields[text_field] = new_text
    line = '\t'.join(old_fields)
    if line.endswith('\n'):
        return line
    else:
        return line + '\n'


def write_modified_version_of_file_to_temp_file(filename, temp_filename, dict_of_kw_to_except_ba_strings,
                                                words_to_rem, words_to_new_except):
    adjusted_num_snippets = 0
    adjusted_num_matches = 0
    original_num_snippets = 0

    temp_f = open(temp_filename, 'w')
    with open(filename, 'r') as f:
        for line in f:
            keyword_list = line[:line.index('\t')].split(',')
            original_num_snippets += 1
            needs_mods = False
            for keyword in keyword_list:
                if keyword in words_to_rem:
                    needs_mods = True
                elif keyword in words_to_new_except:
                    needs_mods = True
            if needs_mods:
                # go through text and figure out what keywords still count
                line_fields = line.split('\t')
                text = line_fields[text_field]
                prev_total_num_matches = int(line_fields[keyword_count_field])

                list_of_actual_matches = get_inds_of_actual_matches_in_text(text, keyword_list,
                                                                            dict_of_kw_to_except_ba_strings,
                                                                            words_to_rem=words_to_rem)
                kwlist_snippet_exactnummatches = \
                    get_list_of_distinct_religious_snippets_in_doc(text, context_window_size,
                                                                   list_of_actual_matches=list_of_actual_matches,
                                                                   include_num_matches_in_each_snippet=True)
                new_lines_to_write = []
                num_still_valid_matches = 0
                for tup in kwlist_snippet_exactnummatches:
                    num_still_valid_matches += tup[2]
                    new_lines_to_write.append(assemble_new_line_given_new_parts_and_prev_line_bits(line_fields,
                                                                                                   tup[0], tup[1],
                                                                                                   tup[2]))
                assert num_still_valid_matches <= prev_total_num_matches
                adjusted_num_matches += num_still_valid_matches

                for new_line in new_lines_to_write:
                    temp_f.write(new_line)
                    adjusted_num_snippets += 1
            else:
                temp_f.write(line)
                adjusted_num_snippets += 1
                start_of_num_matches = None
                for i in range(len(line)):
                    if line[i] == '\t':
                        if start_of_num_matches is None:
                            start_of_num_matches = i + 1
                        else:
                            endplus1_of_num_matches = i
                            break
                adjusted_num_matches += int(line[start_of_num_matches: endplus1_of_num_matches])
    temp_f.close()
    return adjusted_num_snippets, adjusted_num_matches, original_num_snippets


if __name__ == '__main__':
    # prepare keywords
    words_to_remove = {}
    with open(filename_of_words_to_remove_entirely, 'r') as f:
        for line in f:
            word = line.strip().lower()
            if word == '':
                continue
            words_to_remove[word] = 0
    words_to_new_exceptions = {}
    with open(filename_of_words_with_new_exceptions, 'r') as f:
        for line in f:
            line = line.strip().lower()
            if line == '':
                continue
            line = [item.strip() for item in line.split('#')]
            words_to_new_exceptions[line[0]] = line[1:]

    previously_known_keywords_and_exceptions = get_list_of_keywords_and_exceptions(full_keyword_file_to_edit_later)
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

    # modify files
    cur_thread_ind = 0
    temp_filename = dir_to_modify + 'temp.txt'
    total_num_matches_so_far = 0
    total_num_snippets_so_far = 0
    pbar = tqdm(desc='Updating files', total=len(list(glob(dir_to_modify + '*'))))
    while len(list(glob(dir_to_modify + str(cur_thread_ind) + '_1-*'))) > 0:
        num_snippets_included_so_far = 0
        prev_snippets_iterated_through = 0
        first_fname_list = list(glob(dir_to_modify + str(cur_thread_ind) + '_1-*'))
        assert len(first_fname_list) == 1
        cur_fname_list = first_fname_list
        while len(cur_fname_list) > 0:
            assert len(cur_fname_list) == 1
            cur_fname = cur_fname_list[0]
            new_snippets_included, new_matches, num_snippets_in_original_file = \
                write_modified_version_of_file_to_temp_file(cur_fname, temp_filename,
                                                            dict_of_kw_to_except_before_after_strings, words_to_remove,
                                                            words_to_new_exceptions)
            starting_snippet_of_file = num_snippets_included_so_far + 1
            num_snippets_included_so_far += new_snippets_included
            prev_snippets_iterated_through += num_snippets_in_original_file
            new_filename = (dir_to_modify + str(cur_thread_ind) + '_' + str(starting_snippet_of_file) + '-' +
                            str(num_snippets_included_so_far) + '.txt')
            total_num_matches_so_far += new_matches
            os.rename(temp_filename, new_filename)
            if new_filename != cur_fname:
                os.remove(cur_fname)

            cur_fname_list = list(glob(dir_to_modify + str(cur_thread_ind) + '_' +
                                       str(prev_snippets_iterated_through + 1) + '-*'))
            pbar.update(1)
        cur_thread_ind += 1
        total_num_snippets_so_far += num_snippets_included_so_far
    pbar.close()
    print("There are " + str(total_num_matches_so_far) + " valid matches remaining in " +
          str(total_num_snippets_so_far) + " separate snippets.")

    # edit full keywords file to reflect new information
    lines_to_write_to_new_file = []
    with open(full_keyword_file_to_edit_later, 'r') as f:
        for line in f:
            if line == '\n' or line.startswith('#'):
                lines_to_write_to_new_file.append(line)
            else:
                line = line.strip()
                pieces_of_line = [item.strip() for item in line.split('#')]
                if pieces_of_line[0] in words_to_remove:
                    continue
                cur_exceptions = pieces_of_line[1:]
                if pieces_of_line[0] in words_to_new_exceptions:
                    for new_exception in words_to_new_exceptions[pieces_of_line[0]]:
                        if new_exception not in cur_exceptions:
                            cur_exceptions.append(new_exception)
                if len(cur_exceptions) > 0:
                    new_line = pieces_of_line[0] + '\t\t#' + '  #'.join(cur_exceptions) + '\n'
                else:
                    new_line = pieces_of_line[0] + '\n'
                lines_to_write_to_new_file.append(new_line)
    with open(full_keyword_file_to_edit_later, 'w') as f:
        for line in lines_to_write_to_new_file:
            f.write(line)
