import re

# if some religious terms contain others, make sure that the ones
# that are a substring of another come AFTER the longer term
# containing it, in the same batch of regexes

regexes_to_search_for = [
    re.compile('(?:matchterm1)|(?:matchterm2)|(?:matchterm3)'),
    re.compile('(?:matchterm4)|(?:matchterm5)|(?:matchterm6)')
]

regexes_to_consider_false_matches = \
    re.compile('(?:falsematch1)|(?:falsematch2)|(?:falsematch3)')

@outputSchema("bag{tuple(searchterm:chararray, text:chararray)}")
def docmakingudfnonoverlapping(text):
    placeholder_str = '``````````````'
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []

    false_match_inds = [(m.start(0), m.end(0)) for m in
                        regexes_to_consider_false_matches.finditer(text)]
    match_start_end_inds = []
    for regex_to_search_for in regexes_to_search_for:
        new_inds = [(m.start(0), m.end(0)) for m in
                    regex_to_search_for.finditer(text)]
        for i in range(len(new_inds) - 1, -1, -1):
            if text[new_inds[i][0] - 1].isalpha() or \
                    text[new_inds[i][1]].isalpha():
                del new_inds[i]
        inds_to_del = []
        for i in range(len(new_inds) - 1, -1, -1):
            for j in range(len(false_match_inds)):
                #assert i < len(new_inds), text
                if new_inds[i][0] >= false_match_inds[j][0] and \
                        new_inds[i][1] <= false_match_inds[j][1]:
                    inds_to_del.append(i)  # it's a false match
        for ind in inds_to_del:
            del new_inds[ind]
        new_list_pointer = 0
        big_list_pointer = 0
        while new_list_pointer < len(new_inds):
            if big_list_pointer >= len(match_start_end_inds):
                while new_list_pointer < len(new_inds):
                    match_start_end_inds.append(new_inds[new_list_pointer])
                    new_list_pointer += 1
                break
            else:
                if match_start_end_inds[big_list_pointer][0] >= \
                        new_inds[new_list_pointer][0]:
                    match_start_end_inds.insert(big_list_pointer,
                                                new_inds[new_list_pointer])
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
        string_matches.insert(0, text[starting_ind_of_match:
                                      end_ind_of_match_plus_1])
        text = text[:starting_ind_of_match] + placeholder_str + \
               text[end_ind_of_match_plus_1:]
    # ideally, this would be more types of whitespace, but pig only
    # does space in its TOKENIZE method
    tokenized_text = text.split(' ')
    match_inds = []
    matches_found_so_far = 0
    for i in range(len(tokenized_text)):
        while placeholder_str in tokenized_text[i]:
            match_inds.append(i)
            tokenized_text[i] = \
                tokenized_text[i].replace(placeholder_str,
                                          string_matches[matches_found_so_far],
                                          1)
            matches_found_so_far += 1

    window_size = 30
    prev_match_list_of_words = []
    prev_match_list_religious_terms = []
    for i in range(len(match_inds)):
        match_ind = match_inds[i]
        start_start_ind = max([match_ind - window_size, 0])
        if i > 0:
            # adjust start ind to just past the previous match ind, if needed
            start_start_ind = max([start_start_ind, match_inds[i - 1] + 1])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        prev_match_list_religious_terms.append(string_matches[i])
        if i < len(match_inds) - 1:
            next_match_window_start_ind = match_inds[i + 1] - window_size
            if end_end_ind > next_match_window_start_ind:
                # the matches overlap, so add less to this one
                if next_match_window_start_ind <= match_ind + 1:
                    # just add the words before this match, since the starting
                    # window for the next match will have this match's index
                    # (+1) as its starting point
                    prev_match_list_of_words += \
                        (tokenized_text[start_start_ind:start_end_ind])
                else:
                    # add the full set of words before this match, as well as
                    # some of the ones after it
                    prev_match_list_of_words += \
                        (tokenized_text[start_start_ind:start_end_ind] +
                         tokenized_text[end_start_ind:
                                        next_match_window_start_ind])
            else:
                prev_match_list_of_words += \
                    (tokenized_text[start_start_ind:start_end_ind] +
                     tokenized_text[end_start_ind:end_end_ind])
                bag_to_return.append(
                    ("_".join(prev_match_list_religious_terms),
                     " ".join(prev_match_list_of_words)))
                prev_match_list_of_words = []
                prev_match_list_religious_terms = []
        else:
            # we're on the last match of the document, so don't bother
            # resetting prev_match lists
            prev_match_list_of_words += \
                (tokenized_text[start_start_ind:start_end_ind] +
                 tokenized_text[end_start_ind:end_end_ind])
            bag_to_return.append(("_".join(prev_match_list_religious_terms),
                                  " ".join(prev_match_list_of_words)))
    return bag_to_return