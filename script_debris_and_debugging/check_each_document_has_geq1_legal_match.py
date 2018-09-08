import sys
import os
import re


directory_of_samples = sys.argv[1]
filename_of_keywords = sys.argv[2]


false_matches = []


with open(filename_of_keywords, "r") as f:
    keywords = []
    for line in f:
        if line.strip().startswith("#") or line.strip() == '':
            continue
        else:
            line = line.strip()
            line = line.split('#')
            keywords.append(line[0].strip())
            for remaining_phrase in line[1:]:
                remaining_phrase = remaining_phrase.strip()
                if remaining_phrase != '':
                    false_matches.append(remaining_phrase)
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


loose_false_match_regex = ''
for word in false_matches[:-1]:
    loose_false_match_regex += '(?:' + word + ")|"
loose_false_match_regex += '(?:' + false_matches[-1] + ')'
loose_false_match_regex = re.compile(loose_false_match_regex)


keyword_to_contexts = {}
for doc in all_sampled_docs:
    match_inds = [(m.start(0), m.end(0)) for m in loose_regex.finditer(doc)]
    false_match_inds = [(m.start(0), m.end(0)) for m in loose_false_match_regex.finditer(doc)]
    #print("\nFALSE MATCHES:")
    #for false_match in false_match_inds:
    #    print(doc[max([0, false_match[0] - 30]): false_match[1] + 30])
    had_at_least_one_true_match = False
    #print("\nTRUE MATCHES:")
    for match in match_inds:
        start = match[0]
        end_plus_1 = match[1]
        # figure out whether this is actually a match or not
        if start != 0 and doc[start - 1].isalpha():
            continue
        if end_plus_1 != len(doc) and doc[end_plus_1].isalpha():
            continue
        need_to_continue = False
        for false_match in false_match_inds:
            if start >= false_match[0] and end_plus_1 <= false_match[1]:
                need_to_continue = True  # this one's actually a false match
                break
        if need_to_continue:
            continue
        had_at_least_one_true_match = True
        #print(doc[max([0, match[0] - 30]): match[1] + 30])
        keyword_matched = doc[start:end_plus_1]
        context = doc[max(0, start - 30):min(end_plus_1 + 30, len(doc))]
        try:
            keyword_to_contexts[keyword_matched].append(context)
        except:
            keyword_to_contexts[keyword_matched] = [context]
    assert had_at_least_one_true_match, doc
    #input()


alphabetized_found_keywords = sorted([key for key in keyword_to_contexts.keys()])
with open("sample_contexts.txt", "w") as f:
    for word in alphabetized_found_keywords:
        f.write(word + " contexts:\n")
        for context in keyword_to_contexts[word]:
            f.write('\t' + context + '\n')
        f.write('\n')
