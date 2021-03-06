import sys
import os
import re
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid
from make_pig_script_from_template import make_keyword_tuples


if __name__ == '__main__':
    output_name = sys.argv[1]
    temp_results_dir = output_name + "-temp/"
    if not os.path.isdir(temp_results_dir):
        os.makedirs(temp_results_dir)
    total_num_files = str(sys.argv[2])
    window_size = int(sys.argv[3])
    which_file_am_i = sys.argv[4]
    output_filename = output_name + ".txt"
    counter_filename = temp_results_dir + "match_counter.txt"
    if os.path.isfile(counter_filename):
        with open(counter_filename, "r") as f:
            match_file_counter = int(f.readline().strip())
    else:
        match_file_counter = 0


    keywords, strings_to_avoid_for_keyword = \
                get_keywords_and_keywords_strs_to_avoid("get_cooccurrence_words_words_to_search.txt")
    keyword_tuples = make_keyword_tuples(keywords, strings_to_avoid_for_keyword)
    keyword_tuples = [(kt[0][1:-1].replace('\\\\', '\\').replace('\\\'', '\''),
                       kt[1][1:-1], kt)
                      for kt in keyword_tuples]
    regexes_to_search_for = [re.compile(kt[1]) for kt in keyword_tuples]


def get_full_file_contents():
    full_file_str = ''
    for line in sys.stdin:
        full_file_str += line
    return full_file_str


def get_list_of_document_matches(full_file_str):
    is_house_or_senate = full_file_str.split('\n')
    if is_house_or_senate[-1].strip() == '':
        is_house_or_senate = is_house_or_senate[:-1]
    is_house_or_senate = [doc[:doc.index("````````")] for doc in is_house_or_senate]
    is_house_or_senate = [".senate.gov" in tag or ".house.gov" in tag for tag in is_house_or_senate]

    documents = full_file_str.split('````````')
    documents = documents[1:]
    for i in range(len(documents)):
        document = documents[i]
        if document.rfind('\n') == -1:
            end_index = len(document) - 9
        else:
            end_index = document.rfind('\n') - 9
        document = document[1: end_index]
        if document.startswith(chr(1)):
            document = document[1:]
        if chr(1) in document:
            document = document[:document.index(chr(1))]
        documents[i] = document

    assert len(documents) == len(is_house_or_senate)

    documents_to_keep = []
    for i in range(len(is_house_or_senate)):
        if is_house_or_senate[i]:
            documents_to_keep.append(documents[i])
    return documents_to_keep


def make_document_summary_file(text, document_num, searchword_matchcount_dict):
    f = open(temp_results_dir + "temp" + which_file_am_i + "-" + str(document_num) + ".txt", "w")
    placeholder_str = '````````'
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
    if len(match_start_end_inds) == 0:
        print("WARNING: a document that had been selected as a match just turned up as no match.")
        f.close()
        return
    string_matches = []
    for match_ind in range(len(match_start_end_inds) - 1, -1, -1):
        match_inds = match_start_end_inds[match_ind]
        starting_ind_of_match = match_inds[0]
        end_ind_of_match_plus_1 = match_inds[1]
        string_matches.insert(0, text[starting_ind_of_match:end_ind_of_match_plus_1])
        text = text[:starting_ind_of_match] + placeholder_str + text[end_ind_of_match_plus_1:]
    tokenized_text = text.split()
    match_inds = []
    num_matches_found_so_far = 0
    for i in range(len(tokenized_text)):
        while placeholder_str in tokenized_text[i]:
            match_inds.append(i)
            tokenized_text[i] = tokenized_text[i].replace(placeholder_str,
                                                          string_matches[num_matches_found_so_far], 1)
            num_matches_found_so_far += 1
        tokenized_text[i] = tokenized_text[i].strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
    for i in range(len(tokenized_text) - 1, -1, -1):
        foundword = tokenized_text[i]
        if '/' in foundword:
            foundwords = foundword.split('/')
            for j in range(len(foundwords) - 1, -1, -1):
                foundwords[j] = foundwords[j].strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
            tokenized_text[i] = " ".join(foundwords)

    for i in range(len(match_inds)):
        match_ind = match_inds[i]
        start_start_ind = max([match_ind - window_size, 0])
        start_end_ind = match_ind
        end_start_ind = match_ind + 1
        end_end_ind = end_start_ind + window_size
        match_words = tokenized_text[start_start_ind:start_end_ind] + tokenized_text[end_start_ind:end_end_ind]
        search_word = string_matches[i]
        word_to_count = {}
        words_added = {}
        for word in match_words:
            words = word.split(" ")
            for word2 in words:
                if word2 != '':
                    try:
                        word_to_count[word2] += 1
                    except:
                        word_to_count[word2] = 1
                    words_added[word2] = 1
        for word in words_added.keys():
            f.write(search_word + "\t" + word + "\t" + str(word_to_count[word]) + "\n")
        try:
            searchword_matchcount_dict[search_word] += len(match_words)
        except:
            searchword_matchcount_dict[search_word] = len(match_words)
    f.close()
    return searchword_matchcount_dict


def aggregate_all_docs_in_file(total_num_docs, searchword_matchcount_dict):
    f = open(temp_results_dir + "temp" + which_file_am_i + ".txt", "w")
    searchword_foundword_dict = {}
    for i in range(total_num_docs):
        with open(temp_results_dir + "temp" + which_file_am_i + "-" + str(i) + ".txt", "r") as smallf:
            for line in smallf:
                three_pieces = line.strip().split('\t')
                searchword = three_pieces[0]
                foundword = three_pieces[1].strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
                count = int(three_pieces[2])
                foundword = foundword.strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
                if foundword.strip() != '':
                    try:
                        foundword_count_dict = searchword_foundword_dict[searchword]
                        try:
                            foundword_count_dict[foundword] += count
                        except:
                            foundword_count_dict[foundword] = count
                    except:
                        searchword_foundword_dict[searchword] = {foundword: count}
    for searchword in searchword_foundword_dict.keys():
        foundword_count_dict = searchword_foundword_dict[searchword]
        for foundword in foundword_count_dict.keys():
            count = foundword_count_dict[foundword]
            f.write(searchword + "\t" + foundword + "\t" + str(count) + "\t" +
                    str(searchword_matchcount_dict[searchword]) + "\n")
    f.close()


def remove_all_subsummary_files(total_num_docs):
    for document_num in range(total_num_docs):
        if os.path.isfile(temp_results_dir + "temp" + which_file_am_i + "-" + str(document_num) + ".txt"):
            os.remove(temp_results_dir + "temp" + which_file_am_i + "-" + str(document_num) + ".txt")


def main():
    print("Starting to count up cooccurrence words for documents in nonempty file " + str(int(which_file_am_i) + 1) +
          " / " + str(total_num_files))
    documents = get_list_of_document_matches(get_full_file_contents())
    global match_file_counter
    match_file_counter += len(documents)
    with open(counter_filename, "w") as f:
        f.write(str(match_file_counter))
    searchword_matchcount_dict = {}
    for i in range(len(documents)):
        searchword_matchcount_dict = make_document_summary_file(documents[i], i, searchword_matchcount_dict)
    aggregate_all_docs_in_file(len(documents), searchword_matchcount_dict)
    remove_all_subsummary_files(len(documents))
    if int(which_file_am_i) == int(total_num_files) - 1:
        print("Found " + str(match_file_counter) + " matching documents in total.")


if __name__ == '__main__':
    main()
