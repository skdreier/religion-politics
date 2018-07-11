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
    try:
        text = text.decode('utf-8')
    except:
        text = str(text).strip()
        if text == '' or text == "None":
            return []
    matches = re.findall(regex_to_match, text, flags=re.IGNORECASE)
    bag_to_return = []
    if len(matches) == 0:
        return bag_to_return
    for match in matches:
        text = text.replace(match, "THISWASAREGEXMATCHSOREMOVEIT", 1)
    tokenized_text = text.split()
    match_inds = []
    for i in range(len(tokenized_text)):
        if "THISWASAREGEXMATCHSOREMOVEIT" in tokenized_text[i]:
            match_inds.append(i)
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
    return text
