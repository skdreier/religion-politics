import sys
import os
import re
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid
from make_pig_script_from_template import make_keyword_tuples

results_dir = 'script_output/'
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
output_filename = results_dir + sys.argv[1] + ".csv"
total_num_files = str(sys.argv[2])
filename_containing_word = sys.argv[3]

word_count_list = []
for line in sys.stdin:  # line is formatted as foundword    foundwordcount, possibly with some parentheses
    line = line.strip()
    if line == '':
        continue
    line = line.split()
    getting_word = True
    for block in line:
        if block != '':
            if getting_word:
                word = block
            else:
                count = block
                actual_count = ''
                for char in count:
                    if char.isdigit():
                        actual_count += char
                count = actual_count
                word_count_list.append((word, count))
            getting_word = not getting_word

num_lines_so_far = 0
if os.path.isfile(output_filename):
    with open(output_filename, "r") as f:
        for line in f:
            num_lines_so_far += 1
else:
    with open(output_filename, "w") as f:
        f.write("foundword,numcorpusdocsfoundwordappearsin\n")

print("Collecting information from nonempty file " + str(num_lines_so_far + 1) + " / " + total_num_files)

with open(output_filename, "a") as f:
    for word_count in word_count_list:
        word = word_count[0]
        count = word_count[1]
        f.write(word + "," + count + "\n")
