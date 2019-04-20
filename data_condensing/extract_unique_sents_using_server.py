from pycorenlp import StanfordCoreNLP
from tqdm import tqdm
from glob import glob
import os
import shutil
from math import ceil


port_stanford_corenlp_server_running_on = 9000
data_top_level_dir = '/data1/sofias6/dotgov/'
log_filename = 'unique_sentences.log'
output_sent_dir = '/data1/sofias6/dotgov_unique_sentences/'
sents_per_file = 10000


def test_tokenizer():
    text = 'This is a test sentence. Following is another test sentence.'
    output_json = nlp.annotate(text, properties={'annotators': 'tokenize,ssplit', 'outputFormat': 'json'})
    for sent in output_json['sentences']:
        start_offset = sent['tokens'][0]['characterOffsetBegin']
        end_offset = sent['tokens'][-1]['characterOffsetEnd']
        sent_str = text[start_offset:end_offset]


def write_message_to_log_file(message, print_message_too=False):
    with open(log_filename, 'a') as f:
        f.write(message + '\n')
    if print_message_too:
        print(message)


# we assume that each directory will contain either ONLY directories or ONLY files
def contains_files(dir_name):
    if not dir_name.endswith('/'):
        dir_name += '/'
    first_contents_pathname = None
    for filename in glob(dir_name + '*'):
        first_contents_pathname = filename
        break
    if first_contents_pathname is None:
        write_message_to_log_file('Warning: Directory ' + dir_name + ' has no contents', print_message_too=True)

    else:
        if os.path.isfile(first_contents_pathname):
            return True
        else:
            return False


def get_list_of_all_lowest_level_subdirs(dir_name):
    if not dir_name.endswith('/'):
        dir_name = dir_name + '/'
    if not contains_files(dir_name):
        list_to_return = []
        for subdir in glob(dir_name + '*'):
            list_to_return += get_list_of_all_lowest_level_subdirs(subdir)
        return list_to_return
    else:
        # this is a lowest-level subdir
        return [dir_name]


def get_total_number_of_files_in_dir(dir_name):
    total_num_files = 0
    for name_of_dir_containing_files in get_list_of_all_lowest_level_subdirs(dir_name):
        if not name_of_dir_containing_files.endswith('/'):
            name_of_dir_containing_files += '/'
        total_num_files += len(list(glob(name_of_dir_containing_files + '*')))
    return total_num_files


class DocIterator:
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        line_counter = 0
        with open(self.filename, 'r') as f:
            for line in f:
                line_counter += 1
                line = line.strip()
                if len(line) == 0:
                    continue
                list_of_fields = line.split(chr(1))
                yield list_of_fields[7]
                if line_counter % 10000 == 0:
                    write_message_to_log_file("\t" + str(line_counter) + " docs in file processed so far")


def get_list_of_sents_in_doc(doc):
    list_to_ret = []
    list_of_docs = [doc[i * 100000: (i + 1) * 100000] for i in range(ceil(len(doc) / 100000))]

    for i in range(len(list_of_docs)):
        doc = list_of_docs[i]
        output_json = nlp.annotate(doc, properties={'annotators': 'tokenize,ssplit', 'outputFormat': 'json'})
        sentences = output_json['sentences']
        for j in range(len(sentences)):
            sent = sentences[j]
            if (j == 0 and i > 0) or (j == len(sentences) - 1 and i < len(list_of_docs) - 1):
                # this sentence is going in the retokenization bin
                if j == len(sentences) - 1 and i < len(list_of_docs) - 1:
                    sent_split_start_ind = sent['tokens'][0]['characterOffsetBegin']
                else:
                    sent_split_end_ind = sent['tokens'][-1]['characterOffsetEnd']
                    text = doc[sent_split_start_ind: sent_split_end_ind]
                    output_for_split = \
                        nlp.annotate(text, properties={'annotators': 'tokenize,ssplit', 'outputFormat': 'json'})
                    fixed_split_sentences = output_for_split['sentences']
                    for sent in fixed_split_sentences:
                        keep_sentence, sent = filter_sentence(sent, text)
                        if keep_sentence:
                            start_offset = sent['tokens'][0]['characterOffsetBegin']
                            end_offset = sent['tokens'][-1]['characterOffsetEnd']
                            sent = doc[start_offset:end_offset]
                            list_to_ret.append(sent)
            else:
                keep_sentence, sent = filter_sentence(sent, doc)
                if keep_sentence:
                    start_offset = sent['tokens'][0]['characterOffsetBegin']
                    end_offset = sent['tokens'][-1]['characterOffsetEnd']
                    sent = doc[start_offset:end_offset]
                    list_to_ret.append(sent)
    return list_to_ret


def filter_sentence(sentence_json_dict, doc):
    tokens = sentence_json_dict['tokens']
    if len(tokens) == 0:
        return False, None
    if tokens[0]['word'].startswith('http'):
        tokens = tokens[1:]
    if len(tokens) == 0:
        return False, None
    if tokens[-1]['word'].startswith('http'):
        tokens = tokens[:-1]
    if len(tokens) == 0:
        return False, None
    stripped_sent = doc[tokens[0]['characterOffsetBegin']: tokens[-1]['characterOffsetEnd']].strip()
    if '\t' in stripped_sent or '|' in stripped_sent:
        return False, None
    sentence_json_dict['tokens'] = tokens
    return True, sentence_json_dict


def add_unique_sentences_in_file_to_dict(filename, dict_ind_by_sents, file_ind):
    for doc in iter(DocIterator(filename)):
        sents = get_list_of_sents_in_doc(doc)
        for sent in sents:
            if sent not in dict_ind_by_sents:
                dict_ind_by_sents[sent] = file_ind


def fill_up_dict(dict_ind_by_sents):
    sorted_subdirs = sorted(get_list_of_all_lowest_level_subdirs(data_top_level_dir))
    total_num_files = get_total_number_of_files_in_dir(data_top_level_dir)
    if len(sorted_subdirs) == 0:
        return dict_ind_by_sents
    cur_subdir_ind = 0
    sorted_contents_of_cur_subdir = sorted(list(glob(sorted_subdirs[cur_subdir_ind] + '*')))
    num_files_in_cur_subdir = len(sorted_contents_of_cur_subdir)
    next_pct_to_report = 1
    cur_file_ind = 0
    for i in tqdm(range(total_num_files), total=total_num_files, desc="Collecting sents from files"):
        if cur_file_ind == len(sorted_contents_of_cur_subdir):
            # time for a new subdirectory
            cur_subdir_ind += 1
            sorted_contents_of_cur_subdir = sorted(list(glob(sorted_subdirs[cur_subdir_ind] + '*')))
            write_message_to_log_file('Starting on files in subdirectory ' + sorted_subdirs[cur_subdir_ind] + ' (' +
                                      str(len(dict_ind_by_sents)) + ' unique sents found so far)')
            num_files_in_cur_subdir = len(sorted_contents_of_cur_subdir)
            next_pct_to_report = 1
            cur_file_ind = 0
        filename_to_process = sorted_contents_of_cur_subdir[cur_file_ind]
        add_unique_sentences_in_file_to_dict(filename_to_process, dict_ind_by_sents, i)
        cur_file_ind += 1
        if cur_file_ind * 100 / num_files_in_cur_subdir >= next_pct_to_report:
            write_message_to_log_file(str(int(cur_file_ind * 100 / num_files_in_cur_subdir)) + "% through files in " +
                                      sorted_subdirs[cur_subdir_ind] + ", " + str(len(dict_ind_by_sents)) +
                                      " unique sents found so far")
            next_pct_to_report += 1
    assert cur_file_ind == len(sorted_contents_of_cur_subdir)
    assert cur_subdir_ind == len(sorted_subdirs) - 1
    write_message_to_log_file('Finished filling up dict with unique sents', print_message_too=True)
    return dict_ind_by_sents


def write_sents_dict_unordered(dict_ind_by_sents, total_num_sents_collected=0):
    if total_num_sents_collected == 0:
        total_num_sents_collected = len(dict_ind_by_sents)
        print("Collected " + str(total_num_sents_collected) + " unique sentences.")
    file_dir = output_sent_dir
    if not file_dir.endswith('/'):
        file_dir += '/'
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    file_dir += 'unordered/'
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    intra_file_counter = 0
    cur_file_ind = 0
    cur_open_file = open(file_dir + 'sentences_' + str(cur_file_ind) + '.txt', 'w')
    for sent in tqdm(dict_ind_by_sents.keys(), desc="Writing unordered sents to file", total=total_num_sents_collected):
        if intra_file_counter >= sents_per_file:
            cur_open_file.close()
            cur_file_ind += 1
            cur_open_file = open(file_dir + 'sentences_' + str(cur_file_ind) + '.txt', 'w')
            intra_file_counter = 0
        cur_open_file.write(sent + '\n')
        intra_file_counter += 1
    cur_open_file.close()
    return total_num_sents_collected


def write_sents_dict_ordered(dict_ind_by_sents, total_num_sents_collected=0):
    if total_num_sents_collected == 0:
        total_num_sents_collected = len(dict_ind_by_sents)
        print("Collected " + str(total_num_sents_collected) + " unique sentences.")
    file_dir = output_sent_dir
    if not file_dir.endswith('/'):
        file_dir += '/'
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    file_dir += 'ordered_roughly_by_earliest_appearance/'
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)

    sent_earliestappearance_tups = list(dict_ind_by_sents.items())
    sent_earliestappearance_tups = sorted(sent_earliestappearance_tups, key=(lambda x: x[1]), reverse=False)

    intra_file_counter = 0
    cur_file_ind = 0
    cur_open_file = open(file_dir + 'sentences_' + str(cur_file_ind) + '.txt', 'w')
    for sent_earliestappearance_tup in tqdm(sent_earliestappearance_tups, desc="Writing ordered sents to file",
                                            total=total_num_sents_collected):
        sent = sent_earliestappearance_tup[0]
        if intra_file_counter >= sents_per_file:
            cur_open_file.close()
            cur_file_ind += 1
            cur_open_file = open(file_dir + 'sentences_' + str(cur_file_ind) + '.txt', 'w')
            intra_file_counter = 0
        cur_open_file.write(sent + '\n')
        intra_file_counter += 1
    cur_open_file.close()
    return total_num_sents_collected


def main():
    dict_of_sents_to_ind_of_earliest_file_appearing_in = {}
    dict_of_sents_to_ind_of_earliest_file_appearing_in = \
        fill_up_dict(dict_of_sents_to_ind_of_earliest_file_appearing_in)
    total_num_sents = write_sents_dict_unordered(dict_of_sents_to_ind_of_earliest_file_appearing_in)
    # this'll be even more of a stretch for memory, so we wait to try it
    write_sents_dict_ordered(dict_of_sents_to_ind_of_earliest_file_appearing_in,
                             total_num_sents_collected=total_num_sents)
    extraneous_dir = output_sent_dir
    if not extraneous_dir.endswith('/'):
        extraneous_dir += '/'
    extraneous_dir += 'unordered/'
    shutil.rmtree(extraneous_dir)  # if we've made it here, we'll have the same sentences saved in a useful order
    print("Done.")


if __name__ == '__main__':
    nlp = StanfordCoreNLP('http://localhost:' + str(port_stanford_corenlp_server_running_on))
    test_tokenizer()
    main()
