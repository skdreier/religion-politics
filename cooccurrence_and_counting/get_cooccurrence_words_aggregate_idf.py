import sys
import os
import pickle
import multiprocessing
import datetime
from get_cooccurrence_words_from_matches import get_full_file_contents

which_file_am_i = sys.argv[1]
total_num_files = sys.argv[2]
tag_for_job = sys.argv[3]  # outputdirectory
num_results_to_pull_out = int(sys.argv[4])
num_text_files_to_read_results_from = len(sys.argv) - 5
if num_text_files_to_read_results_from > 0:
    text_filenames = [sys.argv[i] for i in range(5, 5 + num_text_files_to_read_results_from)]
    for i in range(num_text_files_to_read_results_from - 1, -1, -1):
        if text_filenames[i].strip() == '':
            del text_filenames[i]
            num_text_files_to_read_results_from -= 1

pickle_dict_filename = tag_for_job + "-temp/"
if not os.path.isdir(pickle_dict_filename):
    os.makedirs(pickle_dict_filename)


pickle_dict_filename += tag_for_job + "-allwordcounts.pkl"
if num_text_files_to_read_results_from == 0:
    output_directory_name = tag_for_job + "-aggregateddocfrequencies/"
else:
    directory_stub = text_filenames[0][:text_filenames[0].index("-sampledocfrequencies/")]
    output_directory_name = directory_stub + "-aggregateddocfrequencies/"
if os.path.isdir(output_directory_name):
    exit(0)


def get_dict_of_words_to_combine(file_text):
    word_doccount_dict = {}
    list_of_words = []
    for line in file_text.split('\n'):
        line = line.strip()
        if line == '':
            continue
        line = line.split(chr(1))
        word = line[0].strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
        count = int(line[1])
        words = word.split('/')
        for word in words:
            word = word.strip().strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
            # + 1 because we subtracted 1 from all word counts in pig script
            try:
                word_doccount_dict[word] += count + 1
            except:
                word_doccount_dict[word] = count + 1
    return word_doccount_dict


def get_full_file_contents_from_filename(filename):
    full_contents = ''
    with open(filename, "r") as f:
        for line in f:
            full_contents += line
    return full_contents


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


def process_single_file_into_pickle_dict(filename_index):
    print("Starting to process document frequencies for words from file " +
          str(int(which_file_am_i) + filename_index + 1) + " / " + str(total_num_files))
    filename = text_filenames[filename_index]
    words_to_consider_combining = get_dict_of_words_to_combine(get_full_file_contents_from_filename(filename))
    return words_to_consider_combining


def add_words_to_pickle_dict(new_words, pickle_dict):
    for word in new_words.keys():
        try:
            pickle_dict[word] += new_words[word]
        except:
            pickle_dict[word] = new_words[word]
    return pickle_dict


def main():
    pickle_dict = load_pickle_dict()

    if num_text_files_to_read_results_from == 0:
        print("Starting to process document frequencies for words from file " +
              str(int(which_file_am_i) + 1) + " / " + str(total_num_files))
        words_to_consider_combining, = get_dict_of_words_to_combine(get_full_file_contents())
        pickle_dict = add_words_to_pickle_dict(words_to_consider_combining, pickle_dict)
    else:
        pool = multiprocessing.Pool(processes=num_text_files_to_read_results_from)
        list_of_pickle_dicts = pool.map(process_single_file_into_pickle_dict,
                                        range(num_text_files_to_read_results_from))
        for new_pickle_dict in list_of_pickle_dicts:
            pickle_dict = add_words_to_pickle_dict(new_pickle_dict, pickle_dict)

    save_pickle_dict(pickle_dict)
    on_last_batch = (num_text_files_to_read_results_from > 0) and \
                    (int(which_file_am_i) + num_text_files_to_read_results_from >= int(total_num_files))
    if (int(which_file_am_i) == int(total_num_files) - 1) or on_last_batch:
        print("Starting to sort all found words by document frequency at " + str(datetime.datetime.now()))
        sorted_words = [key for key in pickle_dict.keys()]
        sorted_words = sorted(sorted_words, key=(lambda x: pickle_dict[x]), reverse=True)
        print("Finished sorting all found words by document frequency at " + str(datetime.datetime.now()))
        os.makedirs(output_directory_name)
        base_num_words_per_file = int(len(sorted_words) / 100)
        num_words_per_file = [base_num_words_per_file for i in range(99)]
        last_num_words = len(sorted_words) - (99 * base_num_words_per_file)
        if last_num_words > 0:
            num_words_per_file.append(last_num_words)
        word_ind = 0
        print("Starting to write aggregated word counts to file at " + str(datetime.datetime.now()))
        for i in range(len(num_words_per_file)):
            filename = output_directory_name + "docfrequenciespart" + str(i) + ".txt"
            with open(filename, "w") as f:
                for j in range(num_words_per_file[i]):
                    f.write(sorted_words[word_ind] + chr(1) + str(pickle_dict[sorted_words[word_ind]]) + "\n")
                    word_ind += 1
        os.remove(pickle_dict_filename)


if __name__ == '__main__':
    main()
