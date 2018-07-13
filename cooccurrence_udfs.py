"""
Author: Sofia Serrano
"""

import re


@outputSchema("bag{tuple(searchterm:chararray, text:chararray)}")
def docmakingudf(text, term, regex_to_match, window_size):
    try:
        term = term.decode('utf-8')
    except:
        term = str(term)
    try:
        regex_to_match = regex_to_match.decode('utf-8')
    except:
        regex_to_match = str(regex_to_match)
    placeholder_str = '``````````````'
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []

    match_start_end_inds = [(m.start(0), m.end(0)) for m in re.finditer(regex_to_match, text, flags=re.IGNORECASE)]
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
            if i not in match_inds:
                match_inds.append(i)
            tokenized_text[i] = tokenized_text[i].replace(placeholder_str,
                                                          string_matches[num_matches_found_so_far], 1)
            num_matches_found_so_far += 1

    for match_ind in match_inds:
        start_start_ind = max([match_ind - window_size, 0])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        match_str = " ".join(tokenized_text[start_start_ind:start_end_ind] +
                             tokenized_text[end_start_ind:end_end_ind])
        bag_to_return.append((term, match_str))
    return bag_to_return


@outputSchema("document:chararray")
def converttochararray(text):
    try:
        text = text.decode('utf-8')
    except:
        text = str(text)
        if text == "None":
            return ""
    return text.lower()