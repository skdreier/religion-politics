import sys
import os
import re
from make_pig_script_from_template import get_keywords_and_keywords_strs_to_avoid
from make_pig_script_from_template import make_keyword_tuples

keywords, strings_to_avoid_for_keyword = \
            get_keywords_and_keywords_strs_to_avoid("get_keyword_counts_keywords_to_count.txt")
keyword_tuples = make_keyword_tuples(keywords, strings_to_avoid_for_keyword)
keyword_tuples = [(kt[0][1:-1].replace('\\\\', '\\').replace('\\\'', '\''),
                   kt[1][1:-1].replace('\\\\', '\\').replace('\\\'', '\'').replace('\\[', '[')
                   .replace('\\^', '^').replace('\\$', '$').replace('\\.', '.').replace('\\|', '|')
                   .replace('\\?', '?').replace('\\*', '*').replace('\\+', '+').replace('\\(', '(')
                   .replace('\\)', ')'), kt)
                  for kt in keyword_tuples]

results_dir = 'script_output/'
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
output_filename = results_dir + sys.argv[1] + ".csv"
total_num_files = str(sys.argv[2])
filename_containing_word = sys.argv[3]

already_loaded_in_previous_file = False
something_changed_in_file = False

for line in sys.stdin:  # line is just foundwordcount, possibly with some parentheses
    line = line.strip()
    if line == '':
        continue
    count = line
    break

actual_count = ''
for char in count:
    if char.isdigit():
        actual_count += char
count = actual_count

num_lines_so_far = 0
if os.path.isfile(output_filename):
    with open(output_filename, "r") as f:
        for line in f:
            num_lines_so_far += 1
else:
    with open(output_filename, "w") as f:
        f.write("foundword,numcorpusdocsfoundwordappearsin\n")

print("Collecting information from nonempty file " + str(num_lines_so_far + 1) + " / " + total_num_files)

word = filename_containing_word[:filename_containing_word.rfind('/')]
word = word[word.rfind('-') + 1:]
if '_insertnonletterdigitchar_' in word:
    match_for_word = None
    word = word.replace('_insertnonletterdigitchar_', '(?:[^a-z]|[^0-9])')
    for kt in keyword_tuples:
        potential_keyword = kt[0][1:-1].replace("\\'", "'").replace('\\\\', '\\')
        matches = [(m.start(0), m.end(0)) for m in re.finditer(word, potential_keyword)]
        if len(matches) == 1:
            if matches[0][0] == 0 and matches[0][1] == len(potential_keyword):
                assert match_for_word is None
                match_for_word = potential_keyword
    assert match_for_word is not None
    word = match_for_word
with open(output_filename, "a") as f:
    f.write(word + "," + count + "\n")
