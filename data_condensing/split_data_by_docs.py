from extract_unique_sents_using_server import get_list_of_all_lowest_level_subdirs, get_total_number_of_files_in_dir
from tqdm import tqdm
from glob import glob
import os


data_top_level_dir = '/data1/sofias6/dotgov/'
new_data_top_level_dir = '/data1/sofias6/dotgov_by_doc/'


def main():
    sorted_subdirs = sorted(get_list_of_all_lowest_level_subdirs(data_top_level_dir))
    total_num_files = get_total_number_of_files_in_dir(data_top_level_dir)
    if len(sorted_subdirs) == 0:
        return
    cur_subdir_ind = 0
    sorted_contents_of_cur_subdir = sorted(list(glob(sorted_subdirs[cur_subdir_ind] + '*')))
    new_corresponding_subdir = get_and_make_subdir_corr_to_cur_subdir(sorted_subdirs[cur_subdir_ind])
    cur_file_ind = 0
    next_available_doc_ind = 0
    for i in tqdm(range(total_num_files), total=total_num_files, desc="Iteration through original files"):
        if cur_file_ind == len(sorted_contents_of_cur_subdir):
            # time for a new subdirectory
            cur_subdir_ind += 1
            sorted_contents_of_cur_subdir = sorted(list(glob(sorted_subdirs[cur_subdir_ind] + '*')))
            new_corresponding_subdir = get_and_make_subdir_corr_to_cur_subdir(sorted_subdirs[cur_subdir_ind])
            cur_file_ind = 0
            next_available_doc_ind = 0
        filename_to_process = sorted_contents_of_cur_subdir[cur_file_ind]
        next_available_doc_ind = write_docs_in_file_to_own_files(filename_to_process, new_corresponding_subdir,
                                                                 next_available_doc_ind)
        os.remove(filename_to_process)
        cur_file_ind += 1
    print("Done splitting files by docs")


def get_and_make_subdir_corr_to_cur_subdir(subdir_name):
    start_of_subdirs = subdir_name[len(data_top_level_dir):]
    subdirs = start_of_subdirs.split('/')
    cur_subdir = new_data_top_level_dir
    if not cur_subdir.endswith('/'):
        cur_subdir += '/'
    if not os.path.isdir(cur_subdir):
        os.makedirs(cur_subdir)
    for subdir in subdirs:
        if subdir.strip() != '':
            cur_subdir += subdir + '/'
            if not os.path.isdir(cur_subdir):
                os.makedirs(cur_subdir)
    return cur_subdir


def write_docs_in_file_to_own_files(filename, new_subdir, next_available_doc_ind):
    for doc in iter(DocIterator(filename)):
        filename = new_subdir + str(next_available_doc_ind) + '.txt'
        with open(filename, 'w') as f:
            if len(doc) > 0 and doc[-1] == '\n':
                f.write(doc)
            else:
                f.write(doc + '\n')
        next_available_doc_ind += 1
    return next_available_doc_ind


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


if __name__ == '__main__':
    main()
