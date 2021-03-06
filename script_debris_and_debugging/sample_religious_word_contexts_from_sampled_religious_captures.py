import sys
import os
import re


directory_of_samples = sys.argv[1]
filename_of_keywords = sys.argv[2]


with open(filename_of_keywords, "r") as f:
    keywords = []
    for line in f:
        if line.strip().startswith("#") or line.strip() == '':
            continue
        else:
            keywords.append(line.strip())
keywords = sorted(keywords, key=(lambda x: len(x)), reverse=True)


def get_list_of_all_files_in_dir(walk_dir):
    filenames = []
    for root, subdirs, files in os.walk(walk_dir):
        for file in files:
            filenames.append(os.path.join(root, file))
        for subdir in subdirs:
            filenames += get_list_of_all_files_in_dir(os.path.join(root, subdir))
    return filenames


def get_list_of_text_from_file(filename):
    texts = []
    # we assume that the title doesn't start with a digit; if it does, the leading string of digits
    # will be removed
    with open(filename, "r") as f:
        all_lines = f.readlines()
    for line in all_lines:
        line = line.strip().lower()
        if line == '':
            continue
        capture_fields = line.split('\t')
        capture_document = capture_fields[-1]
        if line != '':
            texts.append(capture_document)
    return texts


sample_filenames = get_list_of_all_files_in_dir(directory_of_samples)
all_sampled_docs = []
for filename in sample_filenames:
    all_sampled_docs = all_sampled_docs + get_list_of_text_from_file(filename)


loose_regex = ''
for word in keywords[:-1]:
    loose_regex += word + "|"
loose_regex += keywords[-1]
loose_regex = re.compile(loose_regex)


keyword_to_contexts = {}
for doc in all_sampled_docs:
    match_inds = [(m.start(0), m.end(0)) for m in loose_regex.finditer(doc)]
    had_at_least_one_match = False
    for match in match_inds:
        start = match[0]
        end_plus_1 = match[1]
        # figure out whether this is actually a match or not
        if start != 0 and doc[start - 1].isalpha():
            continue
        if end_plus_1 != len(doc) and doc[end_plus_1].isalpha():
            continue
        had_at_least_one_match = True
        keyword_matched = doc[start:end_plus_1]
        context = doc[max(0, start - 30):min(end_plus_1 + 30, len(doc))]
        try:
            keyword_to_contexts[keyword_matched].append(context)
        except:
            keyword_to_contexts[keyword_matched] = [context]
    assert had_at_least_one_match, doc


alphabetized_found_keywords = sorted([key for key in keyword_to_contexts.keys()])
with open("sample_contexts.txt", "w") as f:
    for word in alphabetized_found_keywords:
        f.write(word + " contexts:\n")
        for context in keyword_to_contexts[word]:
            f.write('\t' + context + '\n')
        f.write('\n')
