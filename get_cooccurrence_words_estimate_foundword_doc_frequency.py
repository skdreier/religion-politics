import sys
import os
import re
import pickle
from get_cooccurrence_words_from_matches import get_full_file_contents
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid
from make_pig_script_from_template import make_keyword_tuples
from make_pig_script_from_template import get_all_regexes

which_file_am_i = sys.argv[1]
total_num_files = sys.argv[2]
tag_for_job = sys.argv[3]  # outputdirectory
num_results_to_pull_out = int(sys.argv[4])

pickle_dict_filename = tag_for_job + "-temp/"
if not os.path.isdir(pickle_dict_filename):
    os.makedirs(pickle_dict_filename)


pickle_dict_filename += tag_for_job + "-idfestimationdict.pkl"
idf_estimate_filename = "script_output/" + tag_for_job + "-foundwordestimatedcorpuscount.csv"
fake_doc_frequency_count_to_add = 5


filename_with_words = "get_keyword_doc_counts_keywords_to_count.txt"


def get_dict_of_words_to_combine(file_text):
    word_doccount_dict = {}
    list_of_words = []
    for line in file_text.split('\n'):
        line = line.strip()
        if line == '':
            continue
        line = line.split(chr(1))
        word = line[0]
        count = int(line[1])
        word_doccount_dict[word] = count
        list_of_words.append(word)
    return word_doccount_dict, chr(1) + chr(1).join(list_of_words) + chr(1)


def load_pickle_dict():
    if os.path.isfile(pickle_dict_filename):
        with open(pickle_dict_filename, "rb") as f:
            pickle_dict = pickle.load(f)
    else:
        pickle_dict = {}
    return pickle_dict


def save_pickle_dict(pickle_dict):
    with open(pickle_dict_filename, "wb") as f:
        pickle.dump(pickle_dict, f)


def make_idf_estimate_file(pickle_dict):
    with open(idf_estimate_filename, "w") as f:
        f.write("foundword,numsampleddocsfoundwordappearsin\n")
        for foundword in pickle_dict.keys():
            f.write(foundword + "," + str(pickle_dict[foundword]) + "\n")


def read_in_tf_dict():
    tf_dict = {}
    # fields in tf doc:
    # searchword, foundword, foundwordcount, numwordsinsearchwordsnippets
    with open("script_output/" + tag_for_job + "-cooccurrencecounts.csv", "r") as f:
        f.readline()  # get header out of the way
        for line in f:
            line = line.strip()
            line = line.split(',')
            foundword = line[1].strip()
            foundwordcount = int(line[2].strip())
            try:
                tf_dict[foundword] += foundwordcount
            except:
                tf_dict[foundword] = foundwordcount
    return tf_dict


def remake_filename_with_words(idf_dict):
    tf_dict = read_in_tf_dict()
    foundword_score_list = []
    for foundword in tf_dict.keys():
        tf = tf_dict.get(foundword, 1)
        df = idf_dict.get(foundword, 1) + fake_doc_frequency_count_to_add
        estimated_score = tf / df
        foundword_score_list.append((foundword, estimated_score))
    foundword_score_list = sorted(foundword_score_list, key=(lambda x: x[1]), reverse=True)
    with open(filename_with_words, "w") as f:
        for foundword_tuple in foundword_score_list[:num_results_to_pull_out]:
            f.write(foundword_tuple[0] + "\n")


def main():
    print("Starting to estimate foundword document frequencies from nonempty file " + str(int(which_file_am_i) + 1) +
          " / " + str(total_num_files))
    words_to_consider_combining, all_words_string = get_dict_of_words_to_combine(get_full_file_contents())
    pickle_dict = load_pickle_dict()

    keywords, strings_to_avoid_for_keyword = \
        get_keywords_and_keywords_strs_to_avoid(filename_with_words)
    keyword_tuples = make_keyword_tuples(keywords, strings_to_avoid_for_keyword)
    keyword_tuples = [(kt[0][1:-1].replace('\\\\', '\\').replace('\\\'', '\''),
                       kt[1][1:-1].replace('\\\\', '\\').replace('\\\'', '\'').replace('\\[', '[')
                       .replace('\\^', '^').replace('\\$', '$').replace('\\.', '.').replace('\\|', '|')
                       .replace('\\?', '?').replace('\\*', '*').replace('\\+', '+').replace('\\(', '(')
                       .replace('\\)', ')'), kt)
                      for kt in keyword_tuples]
    all_foundword_regex_expression = re.compile(get_all_regexes(keyword_tuples))

    matches = [(m.start(0), m.end(0)) for m in all_foundword_regex_expression.finditer(all_words_string)]
    for match_inds in matches:
        match_start = match_inds[0]
        match_end_plus_1 = match_inds[1]
        word_start = match_start - 1
        while all_words_string[word_start] != chr(1):
            word_start -= 1
        word_end_plus_1 = match_end_plus_1
        while all_words_string[word_end_plus_1] != chr(1):
            word_end_plus_1 += 1
        raw_word = all_words_string[word_start + 1:word_end_plus_1]
        corresponding_doc_count = words_to_consider_combining[raw_word]
        match_word = all_words_string[match_start:match_end_plus_1]
        try:
            pickle_dict[match_word] += corresponding_doc_count
        except:
            pickle_dict[match_word] = corresponding_doc_count

    save_pickle_dict(pickle_dict)

    if int(which_file_am_i) == int(total_num_files) - 1:
        make_idf_estimate_file(pickle_dict)
        remake_filename_with_words(pickle_dict)


if __name__ == '__main__':
    main()
