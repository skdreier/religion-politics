import os
from glob import glob
from tqdm import tqdm


precount_backup_dir = 'all_religious_word_contexts_backup/'
postcount_dir = 'all_religious_word_contexts/'


if not precount_backup_dir.endswith('/'):
    precount_backup_dir += '/'
if not postcount_dir.endswith('/'):
    postcount_dir += '/'


filenames_in_original_dir = list(glob(precount_backup_dir + '*'))
filenames_in_new_dir = list(glob(postcount_dir + '*'))


filenames_in_original_not_in_new = []
total_num_chars_in_original = 0
total_num_lines_in_original = 0
for filename in tqdm(filenames_in_original_dir, desc='Collecting original dir info'):
    if postcount_dir + filename[len(precount_backup_dir):] not in filenames_in_new_dir:
        filenames_in_original_not_in_new.append(filename)
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            for line in f:
                total_num_lines_in_original += 1
                total_num_chars_in_original += len(line)


filenames_in_new_not_in_original = []
total_num_chars_in_new = 0
total_num_lines_in_new = 0
total_num_matches_registered = 0
num_fields_per_line = None
for filename in tqdm(filenames_in_new_dir, desc='Collecting new dir info'):
    if precount_backup_dir + filename[len(postcount_dir):] not in filenames_in_original_dir:
        filenames_in_new_not_in_original.append(filename)
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            for line in f:
                total_num_lines_in_new += 1
                total_num_chars_in_new += len(line)
                fields_in_line = line.split('\t')
                if num_fields_per_line is None:
                    num_fields_per_line = len(fields_in_line)
                else:
                    assert num_fields_per_line == len(fields_in_line)
                num_matches_in_line = int(fields_in_line[1])
                total_num_matches_registered += num_matches_in_line


if len(filenames_in_original_not_in_new) > 0:
    print("Filenames in original directory not in new:")
    for fname in filenames_in_original_not_in_new:
        print('\t' + fname)
else:
    print("No filenames in original directory that aren't also in new.")

if len(filenames_in_new_not_in_original) > 0:
    print("Filenames in new directory not in original:")
    for fname in filenames_in_new_not_in_original:
        print('\t' + fname)
else:
    print("No filenames in new directory that aren't also in original.")

assert total_num_lines_in_original == total_num_lines_in_new, '\nTotal num lines in original: ' + \
                                                              str(total_num_lines_in_original) + \
                                                              '\nTotal new lines in new: ' + \
                                                              str(total_num_lines_in_new)
num_new_chars = total_num_chars_in_new - total_num_chars_in_original
avg_new_chars_per_line = num_new_chars / total_num_lines_in_new
print("All lines in new directory had " + str(num_fields_per_line) + " fields per line.")
print("Avg of " + str(avg_new_chars_per_line) + ' extra chars per line in new directory.')
print(str(total_num_matches_registered) + " matches registered in total.")
