import os
import sys


input_dir = sys.argv[1]


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


surt_checksum_url_date_tupledict = {}


def process_file(filename):
    new_full_filename = filename[:filename.rfind('.')] + '-2.txt'
    url_filename = filename[:filename.rfind('.')] + '-urls_and_such.txt'
    num_seminar_occurrences = 0
    total_num_previously_religious_occurrences = 0
    with open(filename, 'r') as f:
        with open(new_full_filename, 'w') as new_full:
            with open(url_filename, 'w') as new_url:
                for line in f:
                    if line.strip() == '':
                        continue
                    triggering_word = line[:line.index('\t')]
                    total_num_previously_religious_occurrences += 1
                    if triggering_word == 'seminar':
                        num_seminar_occurrences += 1
                    else:
                        new_full.write(line)
                        line = line.strip().split('\t')
                        url = line[2]
                        surt = line[3]
                        checksum = line[4]
                        date = line[5]
                        tup = (surt, checksum, url, date)
                        if not tup in surt_checksum_url_date_tupledict:
                            surt_checksum_url_date_tupledict[tup] = 1
                            new_url.write(surt + '\t' + checksum + '\t' + url + '\t' + date + '\n')
    return num_seminar_occurrences, total_num_previously_religious_occurrences


filenames = get_list_of_all_files_in_dir(input_dir)
total_seminar = 0
total_prev_religious = 0
for i in range(len(filenames)):
    print('File ' + str(i + 1) + " / " + str(len(filenames)))
    local_seminar, local_prev_religious = process_file(filenames[i])
    total_seminar += local_seminar
    total_prev_religious += local_prev_religious
print("Found " + str(total_prev_religious) + " previously-considered-religious word matches in total.")
print("Found " + str(total_seminar) + " total previous matches for seminar.")
