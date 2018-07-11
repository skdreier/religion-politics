"""
Author: Sofia Serrano
"""

import sys

window_size = sys.argv[1]
num_terms_to_collect = sys.argv[2]
output_dir_stub = sys.argv[3]

keywords = []
with open("cooccurrence_search_words.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line == '' or line.startswith("#"):
            continue
        keywords.append(line)

assert len(keywords) > 0, ("At least one keyword must be provided in cooccurrence_search_words.txt " +
                           "in order for get_cooccurrence_words.pig to be generated.")

keywords = sorted(keywords, reverse=False)

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


def make_exact_match_regex(inner_keyword):
    # this IS supposed to have single quotes around the string
    regex = "'("
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
for keyword in keywords:
    keyword_tuples.append((make_plain_version_of_term(keyword),
                           make_exact_match_regex(keyword),
                           make_simplified_version_of_keyword(keyword)))

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
                # decide whether to add a comma or semicolon after it
                line_inner = line_inner.rstrip()
                if keyword_ind == len(keyword_tuples) - 1:
                    line_inner += ';\n'
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
