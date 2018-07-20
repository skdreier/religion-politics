"""
Author: Sofia Serrano
Python version: either 2 or 3, both work for this script.

This script is responsible for generating a pig script using information
from both its template and its corresponding text file.

Options for template_to_make argument:
cooccurrence_words
keyword_counts

Steps this script takes:

    1. Figures out what the keywords are in the corresponding text file, filters
       out any duplicates, takes note of any string matches for keywords to exclude,
       and orders the keywords from longest to shortest (to help with regex generation
       later).
    2. For each keyword, generate three versions of it:
           - the keyword with single quotes around it
           - a regex version of the keyword (with single quotes around the regex) taking
             into account things we DON'T want to match to this keyword, including both
             the strings that were provided in the corresponding text file with # AND
             other, longer search keywords that any given shorter keyword might be part
             of (so that we avoid double-matching)
           - a version of the keyword with any non-letter or non-digit characters
             replaced by letters (which will be used in naming directories for output
             files)
    3. Generate pig script, repeating marked sections as necessary and replacing
       INSERT<BLANK>HERE mentions with the appropriate string
"""

import sys

if __name__ == '__main__':
    template_to_make = sys.argv[1]
    if template_to_make == 'keyword_counts':
        corresponding_text_file = "get_keyword_counts_keywords_to_count.txt"
        window_size = 0
        num_terms_to_collect = 0
        output_dir_stub = ''
        use_checksum = sys.argv[2]
    elif template_to_make == 'cooccurrence_words':
        corresponding_text_file = "get_cooccurrence_words_words_to_search.txt"
        window_size = sys.argv[2]
        num_terms_to_collect = sys.argv[3]
        output_dir_stub = sys.argv[4]
        use_checksum = sys.argv[5]
    else:
        print("ERROR: " + template_to_make + " is not a valid template.")
        exit(1)

    if use_checksum.strip() == "None":
        use_checksum = False
    else:
        use_checksum = True


def get_keywords_and_keywords_strs_to_avoid(text_file):
    str_keywords = []
    strs_to_avoid_for_keyword = {}
    with open(text_file, "r") as f:
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
                    previous_words_to_avoid = strs_to_avoid_for_keyword[line]
                    strs_to_avoid_for_keyword[line] = list_of_words_for_dict + previous_words_to_avoid
                except:
                    strs_to_avoid_for_keyword[line] = list_of_words_for_dict
            if line not in str_keywords:
                str_keywords.append(line)
    str_keywords = sorted(str_keywords, key=(lambda x: len(x)), reverse=True)
    return str_keywords, strs_to_avoid_for_keyword


if __name__ == '__main__':
    keywords, strings_to_avoid_for_keyword = get_keywords_and_keywords_strs_to_avoid(corresponding_text_file)

    assert len(keywords) > 0, ("At least one keyword must be provided in " + corresponding_text_file +
                               "in order for pig scripts to be generated successfully.")

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


def make_exact_match_regex(inner_keyword, previous_longer_keywords, strs_to_avoid_for_keyword):
    # this IS supposed to have single quotes around the string
    # first, find whether any longer keywords include this keyword as a substring. If so, we won't actually
    # want to consider matches to the longer keyword to be matches for the shorter keyword as well, so
    # prepend the things we DON'T want to match to the regex.
    # Example: suppose our inner_keyword was "to", but we also had the keywords "tortoise" and "actor",
    # we would want to produce the regular expression
    #                 (?!tortoise)((?<!tor)|(?!toise))((?<!ac)|(?!tor))(to)
    try:
        other_strings_to_avoid = strs_to_avoid_for_keyword[inner_keyword]
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
            regex += "(?:(?<!"
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
    regex += "(?:"
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


def make_keyword_tuples(str_keywords, strs_to_avoid_for_keyword):
    keyword_tuples_of_3 = []
    for i in range(len(str_keywords)):
        keyword = str_keywords[i]
        keyword_tuples_of_3.append((make_plain_version_of_term(keyword),
                                    make_exact_match_regex(keyword, str_keywords[:i], strs_to_avoid_for_keyword),
                                    make_simplified_version_of_keyword(keyword)))
    for i in range(len(str_keywords)):
        kt = keyword_tuples_of_3[i]
        keyword_tuples_of_3[i] = (kt[0], kt[1], kt[2], "'.*" + kt[1][1:-1] + ".*'")

    # NOW resort so that keywords are alphabetical
    keyword_tuples_of_3 = sorted(keyword_tuples_of_3, key=(lambda x: x[0]), reverse=False)
    return keyword_tuples_of_3


if __name__ == '__main__':
    keyword_tuples = make_keyword_tuples(keywords, strings_to_avoid_for_keyword)

###########################################################
##                  Now make pig script                  ##
###########################################################


def fill_in_repeated_line_section(lines_to_repeat_inner, script_inner):
    for keyword_ind in range(len(keyword_tuples)):
        keyword_tuple = keyword_tuples[keyword_ind]
        term_itself = keyword_tuple[0]
        regex_term = keyword_tuple[1]
        simplified_term = keyword_tuple[2]
        pig_regex_term = keyword_tuple[3]
        for line_inner_ind in range(len(lines_to_repeat_inner)):
            line_inner = lines_to_repeat_inner[line_inner_ind]
            line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
            line_inner = line_inner.replace("INSERTREGEXHERE", regex_term)
            line_inner = line_inner.replace("INSERTPIGREGEXHERE", pig_regex_term)
            line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
            if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                # decide whether to add a comma or nothing after it
                line_inner = line_inner.rstrip()
                if ' MATCHES ' in line_inner:
                    if keyword_ind == len(keyword_tuples) - 1:
                        line_inner += ';\n'
                    else:
                        line_inner += ' OR\n'
                else:
                    if keyword_ind == len(keyword_tuples) - 1:
                        line_inner += '\n'
                    else:
                        line_inner += ',\n'
            script_inner.write(line_inner)


def fill_in_repeated_line_section_limited(lines_to_repeat_inner, script_inner, limit):
    adjusted_keyword_groupings = [[] for i in range(limit)]
    for i in range(len(keyword_tuples)):
        adjusted_keyword_groupings[i % limit].append(keyword_tuples[i])
    adjusted_keyword_tuples = []
    for keyword_grouping in adjusted_keyword_groupings:
        term_itself = "_".join([kt[0] for kt in keyword_grouping])
        simplified_term = "_".join([kt[2] for kt in keyword_grouping])
        regex_term = get_all_regexes(keyword_grouping)
        pig_regex_term = "'.*" + regex_term[1:-1] + ".*'"
        adjusted_keyword_tuples.append((term_itself, regex_term, simplified_term, pig_regex_term))

    for keyword_ind in range(len(adjusted_keyword_tuples)):
        keyword_tuple = adjusted_keyword_tuples[keyword_ind]
        term_itself = keyword_tuple[0]
        regex_term = keyword_tuple[1]
        simplified_term = keyword_tuple[2]
        pig_regex_term = keyword_tuple[3]
        for line_inner_ind in range(len(lines_to_repeat_inner)):
            line_inner = lines_to_repeat_inner[line_inner_ind]
            line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
            line_inner = line_inner.replace("INSERTREGEXHERE", regex_term)
            line_inner = line_inner.replace("INSERTPIGREGEXHERE", pig_regex_term)
            line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
            if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                # decide whether to add a comma or nothing after it
                line_inner = line_inner.rstrip()
                if ' MATCHES ' in line_inner:
                    if keyword_ind == len(adjusted_keyword_tuples) - 1:
                        line_inner += ';\n'
                    else:
                        line_inner += ' OR\n'
                else:
                    if keyword_ind == len(adjusted_keyword_tuples) - 1:
                        line_inner += '\n'
                    else:
                        line_inner += ',\n'
            script_inner.write(line_inner)


def get_all_regexes(some_keyword_tuples):
    all_regexes = "'"
    for i in range(len(some_keyword_tuples) - 1):
        regex_with_quotes = some_keyword_tuples[i][1]
        try:
            regex_with_quotes[2:].index('(')
            # there are multiple parentheses within regex, so we need another layer
            all_regexes += "(" + regex_with_quotes[1:-1] + ")|"
        except:
            all_regexes += regex_with_quotes[1:-1] + "|"
    regex_with_quotes = some_keyword_tuples[-1][1]
    try:
        regex_with_quotes[2:].index('(')
        # there are multiple parentheses within regex, so we need another layer
        all_regexes += "(?:" + regex_with_quotes[1:-1] + ")"
    except:
        all_regexes += regex_with_quotes[1:-1]
    all_regexes += "'"
    return all_regexes


if __name__ == '__main__':
    pig_script = open("get_" + template_to_make + ".pig", "w")
    in_repeat_section = False
    limited_repeat_section = False
    limit_on_repeat_section = 0
    collecting_checksum_changes = False
    comment_out_next_operative_line = False
    applying_checksum_changes = False
    next_checksum_change_to_apply = -1
    with open("get_" + template_to_make + "TEMPLATE.pig", "r") as f:
        for line in f:
            if line.startswith("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a"):
                line = line.replace("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a",
                                    "-- Get Cooccurrence Words Pig Script: A")
                pig_script.write(line)
                continue
            elif line.startswith("-- Get Keyword Counts TEMPLATE Pig Script: Template for a"):
                line = line.replace("-- Get Keyword Counts TEMPLATE Pig Script: Template for a",
                                    "-- Get Keyword Counts Pig Script: A")
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
                if "ATMOST" in line and len(keyword_tuples) > int(line.strip()[line.strip().index("ATMOST") + 6:]):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("ATMOST") + 6:])
                else:
                    limited_repeat_section = False
                lines_to_repeat = []
                continue
            elif in_repeat_section and not line.strip().startswith("ENDLINEREPEAT"):
                lines_to_repeat.append(line)
                continue
            elif line.strip().startswith("ENDLINEREPEAT"):
                if limited_repeat_section:
                    fill_in_repeated_line_section_limited(lines_to_repeat, pig_script, limit_on_repeat_section)
                else:
                    fill_in_repeated_line_section(lines_to_repeat, pig_script)
                in_repeat_section = False
                continue
            elif not use_checksum and collecting_checksum_changes:
                if line.strip() != '':
                    line = line[line.index(":") + 2:].strip()
                    thing_to_change = line[:line.index('-->')].strip()
                    thing_to_change_to = line[line.index('-->') + 3:].strip()
                    checksum_changes.append((thing_to_change, thing_to_change_to))
                else:
                    collecting_checksum_changes = False
                    applying_checksum_changes = True
                    next_checksum_change_to_apply = 0
            elif not use_checksum and line.startswith("-- IF NOT BOTHERING WITH CHECKSUM") \
                    and not collecting_checksum_changes:
                part_of_line_with_change = line[line.index(":") + 2:].strip()
                if part_of_line_with_change.startswith("comment the next line out"):
                    comment_out_next_operative_line = True
                else:
                    # we're assuming that each of the next few lines contains -->
                    checksum_changes = []
                    thing_to_change = part_of_line_with_change[:part_of_line_with_change.index('-->')].strip()
                    thing_to_change_to = part_of_line_with_change[part_of_line_with_change.index('-->') + 3:].strip()
                    checksum_changes.append((thing_to_change, thing_to_change_to))
                    collecting_checksum_changes = True
            elif not use_checksum and line.strip() != '' and comment_out_next_operative_line:
                if ';' in line:
                    comment_out_next_operative_line = False
                line = "-- " + line
                line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
                line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                if "INSERTALLREGEXESHERE" in line:
                    all_regexes = get_all_regexes(keyword_tuples)
                    if "INSERTALLREGEXESHERESTARTWITHDOT" in line:
                        line = line.replace("INSERTALLREGEXESHERESTARTWITHDOT", "'.*(?:" + all_regexes[1:-1] + ").*'")
                    else:
                        line = line.replace("INSERTALLREGEXESHERE", all_regexes)
                pig_script.write(line)
                continue
            elif not use_checksum and applying_checksum_changes:
                line = line.replace(checksum_changes[next_checksum_change_to_apply][0],
                                    checksum_changes[next_checksum_change_to_apply][1])
                line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
                line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                if "INSERTALLREGEXESHERE" in line:
                    all_regexes = get_all_regexes(keyword_tuples)
                    if "INSERTALLREGEXESHERESTARTWITHDOT" in line:
                        line = line.replace("INSERTALLREGEXESHERESTARTWITHDOT", "'.*(?:" + all_regexes[1:-1] + ").*'")
                    else:
                        line = line.replace("INSERTALLREGEXESHERE", all_regexes)
                pig_script.write(line)
                next_checksum_change_to_apply += 1
                if next_checksum_change_to_apply == len(checksum_changes):
                    applying_checksum_changes = False
            else:
                line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
                line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                if "INSERTALLREGEXESHERE" in line:
                    all_regexes = get_all_regexes(keyword_tuples)
                    if "INSERTALLREGEXESHERESTARTWITHDOT" in line:
                        line = line.replace("INSERTALLREGEXESHERESTARTWITHDOT", "'.*(?:" + all_regexes[1:-1] + ").*'")
                    else:
                        line = line.replace("INSERTALLREGEXESHERE", all_regexes)
                pig_script.write(line)
    pig_script.close()


    udfs = open("get_" + template_to_make + "_udfs.py", "w")
    in_repeat_section = False
    with open("get_" + template_to_make + "_udfsTEMPLATE.py", "r") as f:
        for line in f:
            if not in_repeat_section and line.strip().startswith("STARTLINEREPEAT"):
                in_repeat_section = True
                if "ATMOST" in line and len(keyword_tuples) > int(line.strip()[line.strip().index("ATMOST") + 6:]):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("ATMOST") + 6:])
                else:
                    limited_repeat_section = False
                lines_to_repeat = []
                continue
            elif in_repeat_section and not line.strip().startswith("ENDLINEREPEAT"):
                lines_to_repeat.append(line)
                continue
            elif line.strip().startswith("ENDLINEREPEAT"):
                fill_in_repeated_line_section(lines_to_repeat, udfs)
                in_repeat_section = False
                continue
            else:
                line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
                line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                if "INSERTALLREGEXESHERE" in line:
                    all_regexes = get_all_regexes(keyword_tuples)
                    if "INSERTALLREGEXESHERESTARTWITHDOT" in line:
                        line = line.replace("INSERTALLREGEXESHERESTARTWITHDOT", "'.*(?:" + all_regexes[1:-1] + ").*'")
                    else:
                        line = line.replace("INSERTALLREGEXESHERE", all_regexes)
                udfs.write(line)
    udfs.close()