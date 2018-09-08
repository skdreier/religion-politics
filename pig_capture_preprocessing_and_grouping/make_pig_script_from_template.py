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
       out any obvious duplicates, takes note of any string matches for keywords to exclude,
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
    elif template_to_make == 'keyword_doc_counts':
        corresponding_text_file = "get_keyword_doc_counts_keywords_to_count.txt"
        window_size = 0
        num_terms_to_collect = 0
        output_dir_stub = ''
        use_checksum = sys.argv[2]
    elif template_to_make == 'initialized_religious_files' or template_to_make == 'filtered_religious_files':
        corresponding_text_file = "../all_religious_words.txt"
        window_size = 0
        num_terms_to_collect = 0
        output_dir_stub = ''
        use_checksum = sys.argv[2]
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
                for i in range(len(words_to_exclude)):
                    words_to_exclude[i] = words_to_exclude[i].strip()
                    if i > 0:
                        assert words_to_exclude[i].rfind('*') == -1, "No asterisks allowed in excluded words"
                line = words_to_exclude[0]
                del words_to_exclude[0]
            else:
                words_to_exclude = []

            assert line.rfind('***') == -1

            accept_anything_before = False
            accept_anything_after = False
            words = []
            word_pieces = line.split('**')
            if len(word_pieces) == 2 and word_pieces[0] == '':
                accept_anything_before = True
                word_base = word_pieces[1]
                words = [word_pieces[1]]
            elif len(word_pieces) > 1:
                word_base = word_pieces[-1]
                words.append(word_base)
                for word_prefix in word_pieces[:len(word_pieces) - 1]:
                    words.append(word_prefix + word_base)
            else:
                word_base = word_pieces[0]
                words = word_pieces
            ending_pieces = word_base.split('*')

            if len(ending_pieces) == 2 and ending_pieces[1] == '':
                accept_anything_after = True
                possible_endings = ['']
                dont_modify_word_list = False
            elif len(ending_pieces) > 1:
                possible_endings = [''] + ending_pieces[1:]
                dont_modify_word_list = False
            else:
                possible_endings = ['']
                dont_modify_word_list = True
            if not dont_modify_word_list:
                prefix_list = words
                words = []
                for prefix in prefix_list:
                    prefix = prefix[:prefix.index('*')]
                    for ending in possible_endings:
                        words.append(prefix + ending)

            if accept_anything_before:
                for i in range(len(words)):
                    words[i] = '*' + words[i]
            if accept_anything_after:
                for i in range(len(words)):
                    words[i] = words[i] + '*'

            personalized_words_to_exclude = [[] for i in range(len(words))]
            for i in range(len(words)):
                word = words[i]
                if accept_anything_before:
                    word = word[1:]
                if accept_anything_after:
                    word = word[:-1]
                for exc_word in words_to_exclude:
                    if word in exc_word:
                        personalized_words_to_exclude[i].append(exc_word)

            for i in range(len(words)):
                word = words[i]
                if word not in str_keywords:
                    str_keywords.append(word)
                    strs_to_avoid_for_keyword[word] = personalized_words_to_exclude[i]
                else:
                    # if this keyword is a duplicate, but still contributed new strings
                    # to avoid, add those into consideration
                    previous_words_to_avoid = strs_to_avoid_for_keyword[word]
                    strs_to_avoid_for_keyword[word] = personalized_words_to_exclude[i] + previous_words_to_avoid

    words_with_nonalpha = []
    only_alpha_words = []
    for word in str_keywords:
        only_alpha = True
        for letter in word:
            if not letter.isalpha():
                only_alpha = False
        if only_alpha:
            only_alpha_words.append(word)
        else:
            words_with_nonalpha.append(word)
    str_keywords = sorted(words_with_nonalpha, key=(lambda x: len(x)), reverse=True) + \
                   sorted(only_alpha_words, key=(lambda x: len(x)), reverse=False)
    return str_keywords, strs_to_avoid_for_keyword


if __name__ == '__main__':
    keywords, strings_to_avoid_for_keyword = get_keywords_and_keywords_strs_to_avoid(corresponding_text_file)

    assert len(keywords) > 0, ("At least one keyword must be provided in " + corresponding_text_file +
                               " in order for pig scripts to be generated successfully.")

###########################################################
##  Make required variations on keywords for pig script  ##
###########################################################


def make_simplified_version_of_keyword(inner_keyword):
    # this is NOT supposed to have single quotes around the string
    simplified_version = ''
    simplified_version += 'insertfakechar_'
    for letter in inner_keyword:
        ind = ord(letter)
        if 48 <= ind <= 57 or 65 <= ind <= 90 or 97 <= ind <= 122:
            # it's a safe character for a filename
            simplified_version += letter
        else:
            simplified_version += '_insertnonletterdigitchar_'
    return simplified_version


def make_exact_match_regex(inner_keyword, phrases_to_exclude, strs_to_avoid_for_keyword):
    # this IS supposed to have single quotes around the string
    # first, find whether any longer keywords include this keyword as a substring. If so, we won't actually
    # want to consider matches to the longer keyword to be matches for the shorter keyword as well, so
    # prepend the things we DON'T want to match to the regex.
    # Example: suppose our inner_keyword was "to", but we also had the keywords "tortoise" and "actor",
    # we would want to produce the regular expression
    #                 (?!tortoise)(?:(?<!tor)|(?!toise))(?:(?<!ac)|(?!tor))to
    try:
        other_strings_to_avoid = strs_to_avoid_for_keyword[inner_keyword]
    except:
        other_strings_to_avoid = []
    phrases_to_exclude = other_strings_to_avoid  # we're no longer filtering by other keywords
    strings_not_to_match_before = []
    if inner_keyword.startswith('*') and inner_keyword.endswith('*'):
        inner_keyword = inner_keyword[1:-1]
        return make_regex(inner_keyword, phrases_to_exclude, True, True)
    elif inner_keyword.startswith('*'):
        inner_keyword = inner_keyword[1:]
        return make_regex(inner_keyword, phrases_to_exclude, True, False)
    elif inner_keyword.endswith('*'):
        inner_keyword = inner_keyword[:-1]
        return make_regex(inner_keyword, phrases_to_exclude, False, True)
    else:
        return make_regex(inner_keyword, phrases_to_exclude, False, False)


def make_regex(inner_keyword, phrases_to_exclude, allow_wildcard_before, allow_wildcard_after):
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

    regex = "'(?:"
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
    if not allow_wildcard_before:
        regex += '(?<![a-z])'
    for letter in inner_keyword:
        if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                or letter == ')' or letter == "'"):
            regex += '\\'
        regex += letter
    if not allow_wildcard_after:
        regex += '(?![a-z])'

    for unmatch in strings_not_to_match_after:
        regex += "(?!"
        for letter in unmatch:
            if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                    or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                    or letter == ')' or letter == "'"):
                regex += '\\'
            regex += letter
        regex += ")"

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


def make_keyword_tuples(str_keywords, strs_to_avoid_for_keyword, check_for_nonalphanumeric=True):
    keyword_tuples_of_3 = []
    for i in range(len(str_keywords)):
        keyword = str_keywords[i]
        keyword_tuples_of_3.append((make_plain_version_of_term(keyword),
                                    make_exact_match_regex(keyword, str_keywords[:i], strs_to_avoid_for_keyword),
                                    make_simplified_version_of_keyword(keyword)))
    if check_for_nonalphanumeric:
        for i in range(len(str_keywords)):
            for j in range(i + 1, len(str_keywords)):
                assert keyword_tuples_of_3[i][2] != keyword_tuples_of_3[j][2], (keyword_tuples_of_3[i][0] + " and " +
                                                                                keyword_tuples_of_3[j][0] +
                                                                                " need to differ by more than just " +
                                                                                "nonalphanumeric characters.")
    for i in range(len(str_keywords)):
        kt = keyword_tuples_of_3[i]
        keyword_tuples_of_3[i] = (kt[0], kt[1], kt[2], "'.*" + kt[1][1:-1] + ".*'")

    return keyword_tuples_of_3


if __name__ == '__main__':
    keyword_tuples = make_keyword_tuples(keywords, {})  # strings_to_avoid_for_keyword)
    word_tuples_without_caveats = []
    word_tuples_with_caveats = []
    all_caveats_sorted = []
    for i in range(len(keywords)):
        keyword = keywords[i]
        try:
            caveats = strings_to_avoid_for_keyword[keyword]
            if len(caveats) == 0:
                word_tuples_without_caveats.append(keyword_tuples[i])
            else:
                word_tuples_with_caveats.append(keyword_tuples[i])
                all_caveats_sorted += caveats
        except:
            word_tuples_without_caveats.append(keyword_tuples[i])
    caveat_phrase_tuples = []
    all_caveats_sorted = sorted(all_caveats_sorted, key=(lambda x: len(x)), reverse=True)
    for i in range(len(all_caveats_sorted)):
        caveat = all_caveats_sorted[i]
        caveat_phrase_tuples.append((make_plain_version_of_term(caveat),
                                     make_exact_match_regex(caveat, all_caveats_sorted[:i], {}),
                                     make_simplified_version_of_keyword(caveat)))
    print("There are " + str(len(keyword_tuples)) + " distinct keywords.")

###########################################################
##                  Now make pig script                  ##
###########################################################


def fill_in_repeated_line_section(lines_to_repeat_inner, script_inner, needs_closure, is_pig,
                                  needs_continuation_char, tuples_to_fill_in_with):
    pig_regex_term = get_all_pig_regexes(tuples_to_fill_in_with)
    just_needs_one_line = False
    for line in lines_to_repeat_inner:
        if "INSERTNOBOOKENDSPIGREGEXHERE" in line or "INSERTPIGREGEXHERE" in line:
            just_needs_one_line = True
    if not just_needs_one_line:
        for keyword_ind in range(len(tuples_to_fill_in_with)):
            keyword_tuple = tuples_to_fill_in_with[keyword_ind]
            term_itself = keyword_tuple[0]
            regex_term = keyword_tuple[1]
            simplified_term = keyword_tuple[2]
            for line_inner_ind in range(len(lines_to_repeat_inner)):
                line_inner = lines_to_repeat_inner[line_inner_ind]

                regex_to_use = regex_term
                pig_regex_to_use = pig_regex_term
                if 'MATCHES' in line_inner:
                    # then make sure both terms end with .*
                    if not regex_to_use.startswith("'.*"):
                        regex_to_use = "'.*" + regex_to_use[1:-1] + ".*'"
                    if not pig_regex_to_use.startswith("'.*"):
                        pig_regex_to_use = "'.*" + pig_regex_to_use[1:-1] + ".*'"
                elif 'REPLACE' in line_inner:
                    # then make sure neither term ends with .*
                    if regex_to_use.startswith("'.*"):
                        regex_to_use = "'" + regex_to_use[3:-3] + "'"
                    if pig_regex_to_use.startswith("'.*"):
                        pig_regex_to_use = "'" + pig_regex_to_use[3:-3] + "'"

                line_inner = line_inner.replace("INSERTNOBOOKENDSPIGREGEXHERE", "'" +
                                                pig_regex_term[pig_regex_term.index(']') + 1:
                                                               pig_regex_term.rfind('[')] + "'")
                line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
                line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
                line_inner = line_inner.replace("INSERTREGEXHERE", regex_to_use)
                line_inner = line_inner.replace("INSERTPIGREGEXHERE", pig_regex_to_use)
                line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
                line_inner = line_inner.replace("INSERTTERMINDEXHERE", str(keyword_ind))
                line_inner = line_inner.replace("INSERTREPEATINDEXHERE", str(keyword_ind))
                if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                    # decide whether to add a comma or nothing after it
                    line_inner = line_inner.rstrip()
                    if is_pig:
                        if keyword_ind == len(tuples_to_fill_in_with) - 1:
                            if needs_closure:
                                line_inner += ';'
                            else:
                                line_inner += ''
                        elif ' MATCHES ' in line_inner:
                            line_inner += ' OR'
                        else:
                            line_inner += ','
                    else:
                        if keyword_ind == len(tuples_to_fill_in_with) - 1:
                            if needs_closure:
                                line_inner += ''
                            else:
                                line_inner += ''
                        else:
                            line_inner += ','
                    if keyword_ind != len(tuples_to_fill_in_with) - 1:
                        if needs_continuation_char:
                            line_inner += ' \\'
                    line_inner += '\n'
                script_inner.write(line_inner)
    else:
        keyword_ind = 0
        tuples_to_fill_in_with = tuples_to_fill_in_with[:1]
        keyword_tuple = tuples_to_fill_in_with[keyword_ind]
        term_itself = keyword_tuple[0]
        regex_term = keyword_tuple[1]
        simplified_term = keyword_tuple[2]
        for line_inner_ind in range(len(lines_to_repeat_inner)):
            line_inner = lines_to_repeat_inner[line_inner_ind]
            line_inner = line_inner.replace("INSERTNOBOOKENDSPIGREGEXHERE", "'" +
                                            pig_regex_term[pig_regex_term.index(']') + 1:
                                                           pig_regex_term.rfind('[')] + "'")
            line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
            line_inner = line_inner.replace("INSERTREGEXHERE", regex_term)
            line_inner = line_inner.replace("INSERTPIGREGEXHERE", pig_regex_term)
            line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
            line_inner = line_inner.replace("INSERTTERMINDEXHERE", str(keyword_ind))
            line_inner = line_inner.replace("INSERTREPEATINDEXHERE", str(keyword_ind))
            if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                # decide whether to add a comma or nothing after it
                line_inner = line_inner.rstrip()
                if is_pig:
                    if keyword_ind == len(tuples_to_fill_in_with) - 1:
                        if needs_closure:
                            line_inner += ';'
                        else:
                            line_inner += ''
                    elif ' MATCHES ' in line_inner:
                        line_inner += ' OR'
                    else:
                        line_inner += ','
                else:
                    if keyword_ind == len(tuples_to_fill_in_with) - 1:
                        if needs_closure:
                            line_inner += ''
                        else:
                            line_inner += ''
                    else:
                        line_inner += ','
                if keyword_ind != len(tuples_to_fill_in_with) - 1:
                    if needs_continuation_char:
                        line_inner += ' \\'
                line_inner += '\n'
            script_inner.write(line_inner)


def fill_in_repeated_line_section_limited(lines_to_repeat_inner, script_inner, limit, needs_closure, is_pig,
                                          needs_continuation_char, constraint_on_regexes_per_line,
                                          tuples_to_fill_in_with):
    if constraint_on_regexes_per_line:
        limit = len(tuples_to_fill_in_with) / limit
        if limit == int(limit):
            limit = int(limit)
        else:
            limit = int(limit) + 1
    adjusted_keyword_groupings = [[] for i in range(limit)]
    # sort keyword tuples by their regex's approximate complexity, measured by number of ( in regex
    # we USED to do this when we'd commonly have really complex regexes with lots of exceptions, but now that we
    # have fewer exceptions in the regexes, we've changed this
    # resorted_keyword_tuples = sorted(keyword_tuples, key=(lambda x: [char for char in x[1]].count('(')), reverse=True)
    resorted_keyword_tuples = sorted(tuples_to_fill_in_with, key=(lambda x: len(x)), reverse=True)

    # for some reason grouping regexes as unevenly as possible seems to run much faster, so that's what we do
    num_each_one_gets = int(len(tuples_to_fill_in_with) * 1.0 / limit)
    num_getting_an_extra = len(tuples_to_fill_in_with) % limit
    counter = 0
    for i in range(limit):
        for j in range(num_each_one_gets):
            adjusted_keyword_groupings[i].append(resorted_keyword_tuples[counter])
            counter += 1
        if i < num_getting_an_extra:
            adjusted_keyword_groupings[i].append(resorted_keyword_tuples[counter])
            counter += 1

    """# fill regexes in in a zig-zag pattern so each group gets a set of regexes of roughly equivalent complexity
    for i in range(len(keyword_tuples)):
        group = i % (limit * 2)
        if group >= limit:
            group = (limit * 2) - group - 1
        adjusted_keyword_groupings[group].append(resorted_keyword_tuples[i])"""

    adjusted_keyword_tuples = []
    for keyword_grouping in adjusted_keyword_groupings:
        term_itself = "_".join([kt[0] for kt in keyword_grouping])
        simplified_term = "_".join([kt[2] for kt in keyword_grouping])
        regex_term = get_all_regexes(keyword_grouping)
        pig_regex_term = get_all_pig_regexes(keyword_grouping)
        adjusted_keyword_tuples.append((term_itself, regex_term, simplified_term, pig_regex_term))

    for keyword_ind in range(len(adjusted_keyword_tuples)):
        keyword_tuple = adjusted_keyword_tuples[keyword_ind]
        term_itself = keyword_tuple[0]
        regex_term = keyword_tuple[1]
        simplified_term = keyword_tuple[2]
        pig_regex_term = keyword_tuple[3]
        for line_inner_ind in range(len(lines_to_repeat_inner)):
            line_inner = lines_to_repeat_inner[line_inner_ind]
            line_inner = line_inner.replace("INSERTNOBOOKENDSPIGREGEXHERE", "'" +
                                            pig_regex_term[pig_regex_term.index(']') + 1:
                                                           pig_regex_term.rfind('[')] + "'")
            line_inner = line_inner.replace("INSERTWINDOWSIZEHERE", str(window_size))
            line_inner = line_inner.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
            line_inner = line_inner.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
            line_inner = line_inner.replace("INSERTTERMHERE", term_itself)
            line_inner = line_inner.replace("INSERTREGEXHERE", regex_term)
            line_inner = line_inner.replace("INSERTPIGREGEXHERE", pig_regex_term)
            line_inner = line_inner.replace("INSERTWORDWITHNOSPECIALCHARSORAPOSTROPHES", simplified_term)
            line_inner = line_inner.replace("INSERTTERMINDEXHERE", str(keyword_ind))
            line_inner = line_inner.replace("INSERTREPEATINDEXHERE", str(keyword_ind))
            if line_inner_ind == len(lines_to_repeat_inner) - 1 and line_inner.strip() != '':
                # decide whether to add a comma or nothing after it
                line_inner = line_inner.rstrip()
                if is_pig:
                    if keyword_ind == len(adjusted_keyword_tuples) - 1:
                        if needs_closure:
                            line_inner += ';'
                        else:
                            line_inner += ''
                    elif ' MATCHES ' in line_inner:
                        line_inner += ' OR'
                    else:
                        line_inner += ','
                else:
                    if keyword_ind == len(adjusted_keyword_tuples) - 1:
                        if needs_closure:
                            line_inner += ''
                        else:
                            line_inner += ''
                    else:
                        line_inner += ','
                if keyword_ind != len(adjusted_keyword_tuples) - 1:
                    if needs_continuation_char:
                        line_inner += ' \\'
                line_inner += '\n'
            script_inner.write(line_inner)


def get_all_regexes(some_keyword_tuples):
    all_regexes_inner = "'[^a-z]"
    for i in range(len(some_keyword_tuples) - 1):
        regex_with_quotes = some_keyword_tuples[i][1][1:-1].replace("(?<![a-z])", '').replace("(?![a-z])", '')
        all_regexes_inner += regex_with_quotes + "|"
    regex_with_quotes = some_keyword_tuples[-1][1][1:-1].replace("(?<![a-z])", '').replace("(?![a-z])", '')
    all_regexes_inner += regex_with_quotes
    all_regexes_inner += "[^a-z]'"
    return all_regexes_inner


def get_single_pig_regex(regex_with_quotes):
    return regex_with_quotes.replace('\\', '\\\\')


def get_all_pig_regexes(some_keyword_tuples):
    all_regexes_inner = "'.*[^a-z](?:"
    for i in range(len(some_keyword_tuples) - 1):
        regex_with_quotes = get_single_pig_regex(some_keyword_tuples[i][1])[1:-1]\
            .replace("(?<![a-z])", '').replace("(?![a-z])", '')
        all_regexes_inner += regex_with_quotes + "|"
    regex_with_quotes = get_single_pig_regex(some_keyword_tuples[-1][1])[1:-1]\
        .replace("(?<![a-z])", '').replace("(?![a-z])", '')
    all_regexes_inner += regex_with_quotes
    all_regexes_inner += ")[^a-z].*'"
    return all_regexes_inner


if __name__ == '__main__':
    pig_script = open("get_" + template_to_make + ".pig", "w")
    in_repeat_section = False
    prev_line = ''
    repeat_section_needs_closure = False
    limited_repeat_section = False
    limit_on_repeat_section = 0
    collecting_checksum_changes = False
    comment_out_next_operative_line = False
    applying_checksum_changes = False
    next_checksum_change_to_apply = -1
    needs_continuation_char = False
    limit_by_regexes_per_line = False
    replace_references_to_single_regex_with_more = False
    set_of_keywords_to_use = "original"
    with open("templates/get_" + template_to_make + "TEMPLATE.pig", "r") as f:
        for line in f:
            if line.startswith("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a"):
                line = line.replace("-- Get Cooccurrence Words TEMPLATE Pig Script: Template for a",
                                    "-- Get Cooccurrence Words Pig Script: A")
                pig_script.write(line)
                prev_line = line
                continue
            elif line.startswith("-- Get Keyword Counts TEMPLATE Pig Script: Template for a"):
                line = line.replace("-- Get Keyword Counts TEMPLATE Pig Script: Template for a",
                                    "-- Get Keyword Counts Pig Script: A")
                pig_script.write(line)
                prev_line = line
                continue
            elif line.startswith("-- Get Keyword Doc Counts TEMPLATE Pig Script: Template for a"):
                line = line.replace("-- Get Keyword Doc Counts TEMPLATE Pig Script: Template for a",
                                    "-- Get Keyword Doc Counts Pig Script: A")
                pig_script.write(line)
                prev_line = line
                continue
            elif line.startswith("-- This template script"):
                prev_line = line
                continue
            elif line.startswith("-- The automatically generated script"):
                line = line.replace("-- The automatically generated script",
                                    "-- This automatically generated script")
                pig_script.write(line)
                prev_line = line
                continue
            elif not in_repeat_section and line.strip().startswith("STARTLINEREPEAT"):
                if ' MATCHES ' in prev_line or ' FOREACH ' in prev_line or ' GENERATE ' in prev_line:
                    is_pig = True
                else:
                    is_pig = False
                in_repeat_section = True
                if '_' in line:
                    tag = line[line.index('_') + 1:line.rfind('_')].lower()
                    if tag == 'onlyfalsematches':
                        tuple_list_to_check = caveat_phrase_tuples
                    elif tag == 'onlymatcheswithcaveats':
                        tuple_list_to_check = word_tuples_with_caveats
                    elif tag == 'onlynocaveatmatches':
                        tuple_list_to_check = word_tuples_without_caveats
                else:
                    tag = "original"
                    tuple_list_to_check = keyword_tuples
                if "ATMOST" in line and len(tuple_list_to_check) > int(line.strip()[line.strip().index("ATMOST") + 6:]):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("ATMOST") + 6:])
                    limit_by_regexes_per_line = False
                elif "REGEXESPERLINE" in line and \
                        len(tuple_list_to_check) > int(line.strip()[line.strip().index("REGEXESPERLINE") + 14:]):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("REGEXESPERLINE") + 14:])
                    limit_by_regexes_per_line = True
                elif "REGEXESPERLINE" in line:
                    if not template_to_make == "initialized_religious_files" and \
                            not template_to_make == 'filtered_religious_files':
                        replace_references_to_single_regex_with_more = True
                    else:
                        limited_repeat_section = False
                else:
                    limited_repeat_section = False
                if prev_line.strip().endswith('\\'):
                    needs_continuation_char = True
                else:
                    needs_continuation_char = False
                if prev_line.rfind('(') > prev_line.rfind(')') or \
                                prev_line.rfind('[') > prev_line.rfind(']') or \
                                prev_line.rfind('{') > prev_line.rfind('}'):
                    repeat_section_needs_closure = False
                else:
                    repeat_section_needs_closure = True
                lines_to_repeat = []
                continue
            elif in_repeat_section and not line.strip().startswith("ENDLINEREPEAT"):
                if ' MATCHES ' in line or ' FOREACH ' in line or ' GENERATE ' in line:
                    is_pig = True
                if replace_references_to_single_regex_with_more:
                    line = line.replace("INSERTREGEXHERE", "INSERTALLREGEXESHERE")
                    line = line.replace("INSERTPIGREGEXHERE", "INSERTALLREGEXESHERESTARTWITHDOT")
                    line = line.replace("INSERTREPEATINDEXHERE", "0")
                lines_to_repeat.append(line)
                prev_line = line
                if replace_references_to_single_regex_with_more:
                    line = line.replace("INSERTWINDOWSIZEHERE", str(window_size))
                    line = line.replace("INSERTNUMTERMSTOCOLLECT", str(num_terms_to_collect))
                    line = line.replace("INSERTOUTPUTDIRSTUBWITHNOAPOSTROPHES", output_dir_stub)
                    if "INSERTALLREGEXESHERE" in line:
                        all_regexes = get_all_regexes(keyword_tuples)
                        if "INSERTALLREGEXESHERESTARTWITHDOT" in line:
                            line = line.replace("INSERTALLREGEXESHERESTARTWITHDOT",
                                                "'.*(?:" + all_regexes[1:-1] + ").*'")
                        else:
                            line = line.replace("INSERTALLREGEXESHERE", all_regexes)
                    pig_script.write(line)
                continue
            elif line.strip().startswith("ENDLINEREPEAT"):
                if replace_references_to_single_regex_with_more:
                    replace_references_to_single_regex_with_more = False
                    in_repeat_section = False
                if limited_repeat_section:
                    fill_in_repeated_line_section_limited(lines_to_repeat, pig_script, limit_on_repeat_section,
                                                          repeat_section_needs_closure, is_pig,
                                                          needs_continuation_char, limit_by_regexes_per_line,
                                                          tuple_list_to_check)
                else:
                    fill_in_repeated_line_section(lines_to_repeat, pig_script, repeat_section_needs_closure, is_pig,
                                                  needs_continuation_char, tuple_list_to_check)
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
                prev_line = line
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
            if line.strip() != '':
                prev_line = line
    pig_script.close()

    udfs = open("get_" + template_to_make + "_udfs.py", "w")
    in_repeat_section = False
    prev_line = ''
    tag = "original"
    with open("templates/get_" + template_to_make + "_udfsTEMPLATE.py", "r") as f:
        for line in f:
            if not in_repeat_section and line.strip().startswith("STARTLINEREPEAT"):
                if ' MATCHES ' in prev_line or ' FOREACH ' in prev_line or ' GENERATE ' in prev_line:
                    is_pig = True
                else:
                    is_pig = False
                in_repeat_section = True
                if "ATMOST" in line and len(keyword_tuples) > int(line.strip()[line.strip().index("ATMOST") + 6:]):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("ATMOST") + 6:])
                    limit_by_regexes_per_line = False
                elif ("REGEXESPERLINE" in line) and \
                        (len(keyword_tuples) > int(line.strip()[line.strip().index("REGEXESPERLINE") + 14:])):
                    limited_repeat_section = True
                    limit_on_repeat_section = int(line.strip()[line.strip().index("REGEXESPERLINE") + 14:])
                    limit_by_regexes_per_line = True
                elif "REGEXESPERLINE" in line:
                    replace_references_to_single_regex_with_more = True
                else:
                    limited_repeat_section = False
                if prev_line.strip().endswith('\\'):
                    needs_continuation_char = True
                else:
                    needs_continuation_char = False
                if prev_line.rfind('(') > prev_line.rfind(')') or \
                                prev_line.rfind('[') > prev_line.rfind(']') or \
                                prev_line.rfind('{') > prev_line.rfind('}'):
                    repeat_section_needs_closure = False
                else:
                    repeat_section_needs_closure = True
                lines_to_repeat = []
                continue
            elif in_repeat_section and not line.strip().startswith("ENDLINEREPEAT"):
                if ' MATCHES ' in line or ' FOREACH ' in line or ' GENERATE ' in line:
                    is_pig = True
                if replace_references_to_single_regex_with_more:
                    line = line.replace("INSERTREGEXHERE", "INSERTALLREGEXESHERE")
                    line = line.replace("INSERTPIGREGEXHERE", "INSERTALLREGEXESHERESTARTWITHDOT")
                    line = line.replace("INSERTREPEATINDEXHERE", "0")
                lines_to_repeat.append(line)
                prev_line = line
                if not replace_references_to_single_regex_with_more:
                    continue
            elif line.strip().startswith("ENDLINEREPEAT"):
                if replace_references_to_single_regex_with_more:
                    replace_references_to_single_regex_with_more = False
                    in_repeat_section = False
                    continue
                if limited_repeat_section:
                    fill_in_repeated_line_section_limited(lines_to_repeat, udfs, limit_on_repeat_section,
                                                          repeat_section_needs_closure, is_pig,
                                                          needs_continuation_char, limit_by_regexes_per_line,
                                                          keyword_tuples)
                else:
                    fill_in_repeated_line_section(lines_to_repeat, udfs, repeat_section_needs_closure, is_pig,
                                                  needs_continuation_char, keyword_tuples)
                in_repeat_section = False
                continue
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
            if line.strip() != '':
                prev_line = line
    udfs.close()
