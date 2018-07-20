"""
Author: Sofia Serrano
"""

import re


regexes_to_search_for = [
    STARTLINEREPEAT
    re.compile(INSERTREGEXHERE)
    ENDLINEREPEAT
]


@outputSchema("bag{tuple(searchterm:chararray, text:chararray)}")
def docmakingudf(text, window_size):
    placeholder_str = '``````````````'
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []

    match_start_end_inds = []
    for regex_to_search_for in regexes_to_search_for:
        new_inds = [(m.start(0), m.end(0)) for m in regex_to_search_for.finditer(text)]
        new_list_pointer = 0
        big_list_pointer = 0
        while new_list_pointer < len(new_inds):
            if big_list_pointer >= len(match_start_end_inds):
                while new_list_pointer < len(new_inds):
                    match_start_end_inds.append(new_inds[new_list_pointer])
                    new_list_pointer += 1
                break
            else:
                if match_start_end_inds[big_list_pointer][0] >= new_inds[new_list_pointer][0]:
                    match_start_end_inds.insert(big_list_pointer, new_inds[new_list_pointer])
                    new_list_pointer += 1
            big_list_pointer += 1
    bag_to_return = []
    if len(match_start_end_inds) == 0:
        return bag_to_return
    string_matches = []
    for match_ind in range(len(match_start_end_inds) - 1, -1, -1):
        match_inds = match_start_end_inds[match_ind]
        starting_ind_of_match = match_inds[0]
        end_ind_of_match_plus_1 = match_inds[1]
        string_matches.insert(0, text[starting_ind_of_match:end_ind_of_match_plus_1])
        text = text[:starting_ind_of_match] + placeholder_str + text[end_ind_of_match_plus_1:]
    # ideally, this would be more types of whitespace, but pig only does space in its TOKENIZE method
    tokenized_text = text.split(' ')
    match_inds = []
    num_matches_found_so_far = 0
    for i in range(len(tokenized_text)):
        while placeholder_str in tokenized_text[i]:
            match_inds.append(i)
            tokenized_text[i] = tokenized_text[i].replace(placeholder_str,
                                                          string_matches[num_matches_found_so_far], 1)
            num_matches_found_so_far += 1

    for i in range(len(match_inds)):
        match_ind = match_inds[i]
        start_start_ind = max([match_ind - window_size, 0])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        match_str = " ".join(tokenized_text[start_start_ind:start_end_ind] +
                             tokenized_text[end_start_ind:end_end_ind])
        bag_to_return.append((string_matches[i], match_str))
    return bag_to_return


@outputSchema("document:chararray")
def converttochararray(text):
    # if the entire document is < <length_threshold> chars long, it's not going to have useful cooccurrences
    # anyway
    length_threshold = 5
    try:
        text = text.decode('utf-8')
    except:
        try:
            text = str(text).strip()
        except:
            return ''
    if text == 'None' or len(text) < length_threshold:
        return ''
    else:
        return text.lower()