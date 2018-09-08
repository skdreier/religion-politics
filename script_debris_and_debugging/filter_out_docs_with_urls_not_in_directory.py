import os
import sys


directory_containing_urls = 'all_religious_captures_urls'
directory_to_match_to_urls = sys.argv[1]
if directory_to_match_to_urls.endswith('/'):
    directory_to_match_to_urls = directory_to_match_to_urls[:-1]
new_dirname = directory_to_match_to_urls + "_postseminar/"
surt_field_ind = 1
checksum_field_ind = 2
url_field_ind = 0
date_field_ind = 3


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


urls_files = get_list_of_all_files_in_dir(directory_containing_urls)
surt_checksum_url_date_tupledict = {}
for i in range(len(urls_files)):
    print("Assembling url dict from file " + str(i + 1) + " / " + str(len(urls_files)))
    with open(urls_files[i], 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            line = line.split('\t')
            surt_checksum_url_date_tupledict[(line[0], line[1], line[2], line[3])] = 1


files_in_dir_to_check = get_list_of_all_files_in_dir(directory_to_match_to_urls)
os.makedirs(new_dirname)
for i in range(len(files_in_dir_to_check)):
    print("Remaking file " + str(i + 1) + " / " + str(len(files_in_dir_to_check)))
    filename = files_in_dir_to_check[i]
    new_filename = new_dirname + filename[filename.rfind('/') + 1:]
    with open(filename, 'r') as f:
        with open(new_filename, 'w') as new_f:
            for line in f:
                if line.strip() == '':
                    continue
                fields = line.split('\t')
                if (fields[surt_field_ind], fields[checksum_field_ind], fields[url_field_ind],
                    fields[date_field_ind]) in surt_checksum_url_date_tupledict:
                    new_f.write(line)
