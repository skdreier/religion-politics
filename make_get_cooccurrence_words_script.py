"""
Author: Sofia Serrano
Python version: either 2 or 3, both work for this script.

This script is responsible for generating get_cooccurrence_words.pig using information
from both get_cooccurrence_wordsTEMPLATE.pig and cooccurrence_search_words.txt.

Steps this script takes:

    1. Figures out what the keywords are in cooccurrence_search_words.txt, filters
       out any duplicates, takes note of any string matches for keywords to exclude,
       and orders the keywords from longest to shortest (to help with regex generation
       later).
    2. For each keyword, generate three versions of it:
           - the keyword with single quotes around it
           - a regex version of the keyword (with single quotes around the regex) taking
             into account things we DON'T want to match to this keyword, including both
             the strings that were provided in cooccurrence_search_words.txt with # AND
             other, longer search keywords that any given shorter keyword might be part
             of (so that we avoid double-matching)
           - a version of the keyword with any non-letter or non-digit characters
             replaced by letters (which will be used in naming directories for output
             files)
    3. Generate pig script, repeating marked sections as necessary and replacing
       INSERT<BLANK>HERE mentions with the appropriate string
"""

import sys

window_size = sys.argv[1]
num_terms_to_collect = sys.argv[2]
output_dir_stub = sys.argv[3]

keywords = []
strings_to_avoid_for_keyword = {}
with open("cooccurrence_search_words.txt", "r") as f:
    for line in f:
        line = line.strip().lower()
        if line == '' or line.startswith("#"):
            continue
        if "#" in line:
            words_to_exclude = line.split('#')
            list_of_words_for_dict = []
            for i in range(len(words_to_exclude)):
                words_to_exclude[i] = words_to_exclude[i].strip()
                if i > 0 and words_to_exclude[i] != '':
                    list_of_words_for_dict.append(words_to_exclude[i])
            line = words_to_exclude[0]
            try:
                # if this keyword is a duplicate, but still contributed new strings
                # to avoid, add those into consideration
                previous_words_to_avoid = strings_to_avoid_for_keyword[line]
                strings_to_avoid_for_keyword[line] = list_of_words_for_dict + previous_words_to_avoid
            except:
                strings_to_avoid_for_keyword[line] = list_of_words_for_dict
        if line not in keywords:
            keywords.append(line)

assert len(keywords) > 1, ("At least two keywords must be provided in cooccurrence_search_words.txt " +
                           "in order for get_cooccurrence_words.pig to be generated successfully.\n" +
                           "(This is due to use of DataFu's BagConcat function, which requires at least " +
                           "two bags as arguments, to concatenate intermediate script results for different " +
                           "keywords. In order to change this, modify get_cooccurrence_wordsTEMPLATE.pig.)")

keywords = sorted(keywords, key=(lambda x: len(x)), reverse=True)

###########################################################
##  Make required variations on keywords for pig script  ##
###########################################################


def make_simplified_version_of_keyword(inner_keyword):
    # this is NOT supposed to have single quotes around the string
    simplified_version = ''
    for letter in inner_keyword:
        ind = ord(letter)
        if 48 <= ind <= 57 or 65 <= ind <= 90 or 97 <= ind <= 122:
            # it's a safe character for a filename
            simplified_version += letter
        else:
            simplified_version += '_insertnonletterdigitchar_'
    return simplified_version


def make_exact_match_regex(inner_keyword, previous_longer_keywords):
    # this IS supposed to have single quotes around the string
    # first, find whether any longer keywords include this keyword as a substring. If so, we won't actually
    # want to consider matches to the longer keyword to be matches for the shorter keyword as well, so
    # prepend the things we DON'T want to match to the regex.
    # Example: suppose our inner_keyword was "to", but we also had the keywords "tortoise" and "actor",
    # we would want to produce the regular expression
    #                 (?!tortoise)((?<!tor)|(?!toise))((?<!ac)|(?!tor))(to)
    try:
        other_strings_to_avoid = strings_to_avoid_for_keyword[inner_keyword]
    except:
        other_strings_to_avoid = []
    previous_longer_keywords += other_strings_to_avoid
    strings_not_to_match_before = []
    for i in range(len(previous_longer_keywords)):
        longer_keyword = previous_longer_keywords[i]
        while inner_keyword in longer_keyword:
            # figure out how to distinguish this shorter keyword from the longer keyword
            starting_ind_of_inner_keyword_in_larger = longer_keyword.index(inner_keyword)
            if starting_ind_of_inner_keyword_in_larger == 0:
                strings_not_to_match_before.append(longer_keyword)
            else:
                strings_not_to_match_before.append((longer_keyword[:starting_ind_of_inner_keyword_in_larger],
                                                    longer_keyword[starting_ind_of_inner_keyword_in_larger:]))
            longer_keyword = longer_keyword[starting_ind_of_inner_keyword_in_larger + len(inner_keyword):]

    regex = "'"
    for unmatch in strings_not_to_match_before:
        if isinstance(unmatch, tuple):
            regex += "((?<!"
            for letter in unmatch[0]:
                if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                        or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                        or letter == ')' or letter == "'"):
                    regex += '\\'
                regex += letter
            regex += ")|"
            include_extra_paren_at_end = True
            unmatch = unmatch[1]
        else:
            include_extra_paren_at_end = False
        regex += "(?!"
        for letter in unmatch:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += ")"
        if include_extra_paren_at_end:
            regex += ")"
    regex += "("
    for letter in inner_keyword:
        if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                or letter == ')' or letter == "'"):
            regex += '\\'
        regex += letter
    regex += ")'"
    return regex


def make_plain_version_of_term(inner_keyword):
    # this IS supposed to have single quotes around the string
    plain = "'"
    for letter in inner_keyword:
        if letter == "'" or letter == '\\':
            plain += '\\'
        plain += letter
    plain += "'"
    return plain


keyword_tuples = []
for i in range(len(keywords)):
    keyword = keywords[i]
    keyword_tuples.append((make_plain_version_of_term(keyword),
                           make_exact_match_regex(keyword, keywords[:i]),
                           make_simplified_version_of_keyword(keyword)))


# NOW resort so that keywords are alphabetical

keyword_tuples = sorted(keyword_tuples, key=(lambda x: x[0]), reverse=False)

###########################################################
##                  Now make pig script                  ##
###########################################################


def fill_in_repeated_line_section(lines_to_repeat_inner, pig_script_inner):
    for keyword_ind in range(len(keyword_tuples)):
        keyword_tuple = keyword_tuples[keyword_ind]
        term_itself = keyword_tuple[0]
        regex_term = keyword_tuple[1]
        simplified_term = keyword_tuple[2]
        for line_inner_ind in range(len(lines_to_repeat_inner)):
            line_inner = lines_to_repeat_inner[line_inner_ind]
            line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
            line_inner = line_inner.replace("INSERTREGEXHERE", regex_term)
            line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
            if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                # decide whether to add a comma or nothing after it
                line_inner = line_inner.rstrip()
                if keyword_ind == len(keyword_tuples) - 1:
                    line_inner += '\n'
                else:
                    line_inner += ',\n'
            pig_script_inner.write(line_inner)


pig_script = open("get_cooccurrence_words.pig", "w")
in_repeat_section = False
with open("get_cooccurrence_wordsTEMPLATE.pig", "r") as f:
    for line in f:
        if line.startswith("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a"):
            line = line.replace("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a",
                                "-- Get Cooccurrence Words Pig Script: A")
            pig_script.write(line)
            continue
        elif line.startswith("-- This template script"):
            continue
        elif line.startswith("-- The automatically generated script"):
            line = line.replace("-- The automatically generated script",
                                "-- This automatically generated script")
            pig_script.write(line)
            continue
        elif not in_repeat_section and line.strip().startswith("STARTLINEREPEAT"):
            in_repeat_section = True
            lines_to_repeat = []
            continue
        elif in_repeat_section and not line.strip().startswith("ENDLINEREPEAT"):
            lines_to_repeat.append(line)
            continue
        elif line.strip().startswith("ENDLINEREPEAT"):
            fill_in_repeated_line_section(lines_to_repeat, pig_script)
            in_repeat_section = False
            continue
        else:
            line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            pig_script.write(line)
pig_script.close()
