import os


dir_to_check = 'word_corpuscounts'


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


all_files = get_list_of_all_files_in_dir(dir_to_check)
total = 0
for i in range(len(all_files)):
    print("Calculating total from file " + str(i + 1) + " / " + str(len(all_files)))
    with open(all_files[i], 'r') as f:
        for line in f:
            if line.strip() == '':
                continue
            total += int(line.split('\t')[1]) + 1

print("Total number of words counted: " + str(total))