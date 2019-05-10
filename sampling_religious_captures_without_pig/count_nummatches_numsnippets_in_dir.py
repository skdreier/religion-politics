from glob import glob
import sys
from tqdm import tqdm

dir_name = sys.argv[1].strip()
if not dir_name.endswith('/'):
    dir_name += '/'


def get_ind_of_4th_tab_from_end(line):
    num_tabs_passed_so_far = 0
    for i in range(len(line) - 1, -1, -1):
        if line[i] == '\t':
            num_tabs_passed_so_far += 1
        if num_tabs_passed_so_far == 4:
            return i


total_num_snippets = 0
total_num_matches = 0
doc_ids = {}
for fname in tqdm(list(glob(dir_name + '*'))):
    with open(fname, 'r') as f:
        for line in f:
            if len(line) < 2:
                continue
            total_num_snippets += 1
            line = line[line.index('\t') + 1:]
            num_matches = int(line[:line.index('\t')])
            total_num_matches += num_matches
            line_id = line[get_ind_of_4th_tab_from_end(line) + 1:]
            doc_ids[line_id] = 0


print('Total num matches: ' + str(total_num_matches))
print('Total num snippets: ' + str(total_num_snippets))
print('Total num page captures: ' + str(len(doc_ids)))
