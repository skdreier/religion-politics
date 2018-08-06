import os
import sys
import pickle
import multiprocessing
from math import ceil

input_dir = sys.argv[1]
output_dir = sys.argv[2]
type_of_freq = sys.argv[3]  # Doc or Corpus
if type_of_freq == "Doc":
    doc_frequency = True
else:
    doc_frequency = False
if not output_dir.endswith('/'):
    output_dir += '/'


default_num_multiprocessing_threads = 80
filestart_counter = 0
in_progress_pkl_filename = "mid-collection_doc_frequency_counts.pkl"


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


def get_list_of_text_from_file(filename):
    texts = []
    # we assume that the title doesn't start with a digit; if it does, the leading string of digits
    # will be removed
    with open(filename, "r") as f:
        all_lines = f.readlines()
    for line in all_lines:
        if line.strip() == '':
            continue
        # find the date, which will be an 8-digit sequence starting with either 20 or 19
        digit_str_in_progress = ''
        starting_ind_of_title = -1
        for char_ind in range(len(line)):
            if len(digit_str_in_progress) == 0:
                if line[char_ind] == '2' or line[char_ind] == '1':
                    digit_str_in_progress = line[char_ind]
            elif len(digit_str_in_progress) == 1:
                if line[char_ind] == '0' or line[char_ind] == '9':
                    digit_str_in_progress += line[char_ind]
                else:
                    digit_str_in_progress = ''
            elif len(digit_str_in_progress) == 4:
                if line[char_ind] == '0' or line[char_ind] == '1':
                    digit_str_in_progress += line[char_ind]
                else:
                    digit_str_in_progress = ''
            elif len(digit_str_in_progress) < 8:
                if line[char_ind].isdigit():
                    digit_str_in_progress += line[char_ind]
                else:
                    digit_str_in_progress = ''
            else:
                if not line[char_ind].isdigit():
                    starting_ind_of_title = char_ind
                    break
        assert len(digit_str_in_progress) == 8, "We didn't find a valid date in this entry"
        if starting_ind_of_title != -1:
            text = line[starting_ind_of_title:].strip().lower()
            if text != '':
                texts.append(text)
    return texts


def make_dict_for_file(local_file_ind):
    file_index = filestart_counter + local_file_ind
    print("Starting to process file " + str(file_index + 1) + " / " + str(len(all_filenames_in_dir)))
    fname_to_process = all_filenames_in_dir[file_index]
    docs_in_file = get_list_of_text_from_file(fname_to_process)
    word_count_dict = {}
    for doc in docs_in_file:
        doc_dict = {}
        doc = doc.split()
        for word in doc:
            word = word.strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
            if word == '':
                continue
            if doc_frequency:
                words = word.split('/')
                for inner_word in words:
                    inner_word = inner_word.strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
                    if inner_word == '':
                        continue
                    doc_dict[inner_word] = 1
            else:
                try:
                    word_count_dict[word] += 1
                except:
                    word_count_dict[word] = 1
        if doc_frequency:
            for word in doc_dict.keys():
                try:
                    word_count_dict[word] += 1
                except:
                    word_count_dict[word] = 1
    return word_count_dict


def try_pool(num_threads):
    global filestart_counter
    try:
        pool = multiprocessing.Pool(processes=num_threads)
        list_of_wordcount_dicts = pool.map(make_dict_for_file, range(num_threads))
        filestart_counter += num_threads
    except:
        pool.close()
        return False
    pool.close()
    return list_of_wordcount_dicts


all_filenames_in_dir = get_list_of_all_files_in_dir(input_dir)
num_batches_to_run = int(ceil(len(all_filenames_in_dir) / default_num_multiprocessing_threads))
master_dict = {}
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
    list_of_wordcount_dicts = got_results
    for wordcount_dict in list_of_wordcount_dicts:
        for word in wordcount_dict.keys():
            try:
                master_dict[word] += wordcount_dict[word]
            except:
                master_dict[word] = wordcount_dict[word]
    with open(in_progress_pkl_filename, "wb") as f:
        pickle.dump(master_dict, f)


if not os.path.isdir(output_dir):
    os.makedirs(output_dir)


all_foundwords = [key for key in master_dict.keys()]
if not doc_frequency:
    words_to_delete = []
    for word in all_foundwords:
        words = word.split('/')
        if len(words) > 1:
            words_to_delete.append(word)
            for inner_word in words:
                inner_word = inner_word.strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
                if inner_word == '':
                    continue
                try:
                    master_dict[inner_word] += 1
                except:
                    master_dict[inner_word] = 1
    for word in words_to_delete:
        all_foundwords.remove(word)
num_words_per_file = int(len(all_foundwords) / 100)


print("Starting to write word frequencies to files.")
word_ind = 0
for i in range(99):
    with open(output_dir + "frequenciespart" + str(i) + ".txt") as f:
        for j in range(num_words_per_file):
            f.write(all_foundwords[word_ind] + chr(1) + str(master_dict[all_foundwords[word_ind]]) + "\n")
            word_ind += 1
with open(output_dir + "frequenciespart99.txt") as f:
    while word_ind < len(all_foundwords):
        f.write(all_foundwords[word_ind] + chr(1) + str(master_dict[all_foundwords[word_ind]]) + "\n")
        word_ind += 1
