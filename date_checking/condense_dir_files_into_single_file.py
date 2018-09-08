# sample usage:
# python condense_dir_files_into_single_file.py /path/to/dir/dont_end_with_slash

import sys
import os

dir_name = sys.argv[1]


output_fname = dir_name + ".txt"


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


filenames = sorted(get_list_of_all_files_in_dir(dir_name))


with open(output_fname, "w") as f:
    for filename in filenames:
        with open(filename, "r") as readf:
            for line in readf:
                if line.strip() != '':
                     f.write(line)

