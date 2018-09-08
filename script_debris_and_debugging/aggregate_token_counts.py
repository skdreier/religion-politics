import sys
import os


dir_name = sys.argv[1]


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


filenames = get_list_of_all_files_in_dir(dir_name)


token_religiouscount_dict = {}
token_fullcount_dict = {}


for i in range(len(filenames)):
    print("Working on file " + str(i + 1) + " / " + str(len(filenames)))
    with open(filenames[i], 'r') as f:
        for line in f:
            if line.strip() == '':
                continue
            line = line.split('\t')
            assert len(line) >= 3, str(line)
            token = line[0].strip('!,.?\'"`/()[]{}#*~|\\<>@$^&:;-_=+')
            try:
                religious_count = int(line[1])
            except:
                assert False, str(line)
            try:
                full_count = int(line[2])
            except:
                if line[2] == '':
                    full_count = 1  # fell through the cracks while counts were being added back in
                else:
                    assert False, str(line)
            try:
                token_religiouscount_dict[token] += religious_count
                token_fullcount_dict[token] += full_count
            except:
                token_religiouscount_dict[token] = religious_count
                token_fullcount_dict[token] = full_count


num_per_new_file = int(len(token_religiouscount_dict) / 100)
end_inds = [i * num_per_new_file for i in range(1, len(token_religiouscount_dict))] + [len(token_religiouscount_dict)]
all_dict_keys = [key for key in token_religiouscount_dict.keys()]
start_ind = 0
for i in range(100):
    print("Writing file " + str(i + 1) + ' / 100')
    new_filename = os.path.join(dir_name, "processed_" + str(i) + ".txt")
    end_ind = end_inds[i]
    with open(new_filename, 'w') as f:
        for j in range(start_ind, end_ind):
            token = all_dict_keys[j]
            f.write(token + '\t' + str(token_religiouscount_dict[token]) + '\t' + str(token_fullcount_dict[token]) +
                    '\t' + str(token_religiouscount_dict[token] / token_fullcount_dict[token]) + '\n')
    start_ind = end_ind
