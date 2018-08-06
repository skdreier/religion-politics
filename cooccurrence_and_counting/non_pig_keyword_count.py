import sys
import os
import re
import multiprocessing
from math import ceil
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid

input_dir = sys.argv[1]
output_filename = sys.argv[2]

default_num_multiprocessing_threads = 40


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


def make_loose_regex(keyword):
    regex = '(?:'
    for letter in keyword:
        if (letter == '[' or letter == '\\' or letter == '^' or letter == '$' or letter == '.'
                or letter == '|' or letter == '?' or letter == '*' or letter == '+' or letter == '('
                or letter == ')'):
            regex += '\\'
        regex += letter
    regex += ')'
    return regex


def make_full_loose_regex_expression(all_keywords):
    regex = ''
    for keyword in all_keywords:
        regex += make_loose_regex(keyword) + "|"
    regex = regex[:-1]
    return regex


def get_list_of_text_from_file(filename):
    texts = []
    # we assume that the title doesn't start with a digit; if it does, the leading string of digits
    # will be removed
    with open(filename, "r") as f:
        all_lines = f.readlines()
    for line in all_lines:
        line = line.strip().lower()
        if line == '':
            continue
        starting_ind_of_title = line.rfind(chr(1))
        assert starting_ind_of_title != -1
        if line != '':
            texts.append((line, starting_ind_of_title))
    return texts


def get_matches(file_index):
    print("Starting work on file " + str(file_index + num_already_covered + 1) + " / " + str(len(all_filenames)))
    filename = all_filenames[file_index + num_already_covered]
    texts_startinginds = get_list_of_text_from_file(filename)

    loose_matches_including_urls = {}
    loose_matches_no_urls = {}
    tight_matches_including_urls = {}
    tight_matches_no_urls = {}

    loose_matches_including_urls_docfreq = {}
    loose_matches_no_urls_docfreq = {}
    tight_matches_including_urls_docfreq = {}
    tight_matches_no_urls_docfreq = {}

    num_docs_with_any_loose_matches = 0
    num_docs_with_loose_matches_in_text = 0
    num_docs_with_any_tight_matches = 0
    num_docs_with_tight_matches_in_text = 0

    for text_startind in texts_startinginds:
        text = text_startind[0]
        startind = text_startind[1]
        match_inds = [(m.start(0), m.end(0)) for m in loose_match_searcher.finditer(text)]
        loose_including_url_doc = {}
        loose_no_url_doc = {}
        tight_including_url_doc = {}
        tight_no_url_doc = {}
        has_loose_match = False
        has_loose_match_in_text = False
        has_tight_match = False
        has_tight_match_in_text = False
        for match_ind_pair in match_inds:
            match_start = match_ind_pair[0]
            match_end = match_ind_pair[1]
            word = text[match_start:match_end]

            loose_including_url_doc[word] = 1
            has_loose_match = True
            try:
                loose_matches_including_urls[word] += 1
            except:
                loose_matches_including_urls[word] = 1
            if match_start >= startind:
                has_loose_match_in_text = True
                loose_no_url_doc[word] = 1
                try:
                    loose_matches_no_urls[word] += 1
                except:
                    loose_matches_no_urls[word] = 1
            is_tight_match = ((match_end == len(text) or not text[match_end].isalpha()) and
                              (match_start == 0 or not text[match_start - 1].isalpha()))
            if is_tight_match:
                has_tight_match = True
                tight_including_url_doc[word] = 1
                try:
                    tight_matches_including_urls[word] += 1
                except:
                    tight_matches_including_urls[word] = 1
                if match_start >= startind:
                    has_tight_match_in_text = True
                    tight_no_url_doc[word] = 1
                    try:
                        tight_matches_no_urls[word] += 1
                    except:
                        tight_matches_no_urls[word] = 1
        for word in loose_including_url_doc.keys():
            loose_matches_including_urls_docfreq[word] = loose_matches_including_urls_docfreq.get(word, 0) + 1
        for word in loose_no_url_doc.keys():
            loose_matches_no_urls_docfreq[word] = loose_matches_no_urls_docfreq.get(word, 0) + 1
        for word in tight_including_url_doc.keys():
            tight_matches_including_urls_docfreq[word] = tight_matches_including_urls_docfreq.get(word, 0) + 1
        for word in tight_no_url_doc.keys():
            tight_matches_no_urls_docfreq[word] = tight_matches_no_urls_docfreq.get(word, 0) + 1
        if has_loose_match:
            num_docs_with_any_loose_matches += 1
        if has_loose_match_in_text:
            num_docs_with_loose_matches_in_text += 1
        if has_tight_match:
            num_docs_with_any_tight_matches += 1
        if has_tight_match_in_text:
            num_docs_with_tight_matches_in_text += 1

    return (loose_matches_including_urls, loose_matches_no_urls, tight_matches_including_urls, tight_matches_no_urls,
            loose_matches_including_urls_docfreq, loose_matches_no_urls_docfreq, tight_matches_including_urls_docfreq,
            tight_matches_no_urls_docfreq, num_docs_with_any_loose_matches, num_docs_with_loose_matches_in_text,
            num_docs_with_any_tight_matches, num_docs_with_tight_matches_in_text)


def try_pool(num_threads):
    global num_already_covered
    try:
        pool = multiprocessing.Pool(processes=num_threads)
        list_of_wordcount_dicts = pool.map(get_matches, range(num_threads))
        num_already_covered += num_threads
    except:
        pool.close()
        return False
    pool.close()
    return list_of_wordcount_dicts


keywords, strs_to_avoid = get_keywords_and_keywords_strs_to_avoid("non_pig_loose_keyword_match.txt")
loose_match_searcher = re.compile(make_full_loose_regex_expression(keywords))
all_filenames = get_list_of_all_files_in_dir(input_dir)
num_already_covered = 0
num_batches_to_run = int(ceil(len(all_filenames) / default_num_multiprocessing_threads))


master_dicts = [{}, {}, {}, {}, {}, {}, {}, {}]
num_docs_w_loose_match = 0
num_docs_w_loose_text_match = 0
num_docs_w_tight_match = 0
num_docs_w_tight_text_match = 0


for batch in range(num_batches_to_run):
    got_results = False
    latest_num_threads = default_num_multiprocessing_threads
    while not got_results:
        got_results = try_pool(latest_num_threads)
        if not got_results:
            latest_num_threads = int(latest_num_threads / 2)
            if latest_num_threads < 1:
                print("Didn't work even with a single thread. Exiting now.")
                exit(1)
    list_of_wordcount_dict_tuples = got_results
    
    for wordcount_dict_tuple in list_of_wordcount_dict_tuples:
        for i in range(8):
            wordcount_dict = wordcount_dict_tuple[i]
            master_dict = master_dicts[i]
            for word in wordcount_dict.keys():
                try:
                    master_dict[word] += wordcount_dict[word]
                except:
                    master_dict[word] = wordcount_dict[word]
        num_docs_w_loose_match += wordcount_dict_tuple[8]
        num_docs_w_loose_text_match += wordcount_dict_tuple[9]
        num_docs_w_tight_match += wordcount_dict_tuple[10]
        num_docs_w_tight_text_match += wordcount_dict_tuple[11]
                    
                    
with open(output_filename, "w") as f:
    f.write("Word,# loose matches in text," +
            "# exact matches in text," +
            "# docs w/ >= 1 loose match in text," +
            "# docs w/ >= 1 exact match in text," +
            "# loose matches in any field," +
            "# exact matches in any field," +
            "# docs w/ >= 1 loose match in any field," +
            "# docs w/ >= 1 exact match in any field\n")
    loose_text = master_dicts[1]
    tight_text = master_dicts[3]
    loose_text_docfreq = master_dicts[5]
    tight_text_docfreq = master_dicts[7]

    loose_anywhere = master_dicts[0]
    tight_anywhere = master_dicts[2]
    loose_anywhere_docfreq = master_dicts[4]
    tight_anywhere_docfreq = master_dicts[6]

    total_num_loose_text_matches = 0
    total_num_exact_text_matches = 0
    total_num_loose_matches = 0
    total_num_exact_matches = 0
    for keyword in keywords:
        total_num_loose_text_matches += loose_text.get(keyword, 0)
        total_num_exact_text_matches += tight_text.get(keyword, 0)
        total_num_loose_matches += loose_anywhere.get(keyword, 0)
        total_num_exact_matches += tight_anywhere.get(keyword, 0)

    f.write("AnySearchWord," + str(total_num_loose_text_matches) + "," +
            str(total_num_exact_text_matches) + "," +
            str(num_docs_w_loose_text_match) + "," +
            str(num_docs_w_tight_text_match) + "," +
            str(total_num_loose_matches) + "," +
            str(total_num_exact_matches) + "," +
            str(num_docs_w_loose_match) + "," +
            str(num_docs_w_tight_match) + "\n")

    for keyword in keywords:
        f.write(keyword + "," + str(loose_text.get(keyword, 0)) + "," +
                str(tight_text.get(keyword, 0)) + "," +
                str(loose_text_docfreq.get(keyword, 0)) + "," +
                str(tight_text_docfreq.get(keyword, 0)) + "," +
                str(loose_anywhere.get(keyword, 0)) + "," +
                str(tight_anywhere.get(keyword, 0)) + "," +
                str(loose_anywhere_docfreq.get(keyword, 0)) + "," +
                str(tight_anywhere_docfreq.get(keyword, 0)) + "\n")
