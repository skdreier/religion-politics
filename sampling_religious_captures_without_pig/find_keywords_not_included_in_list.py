kw_file_that_should_include_all = 'all_religious_words.txt'
subset_file = 'all_logged_keywords.txt'


all_keywords = []
with open(kw_file_that_should_include_all, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        line = line.split('#')[0].strip()
        all_keywords.append(line)


subset_kws = []
with open(subset_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        line = line.split('#')[0].strip()
        subset_kws.append(line)

        if line not in all_keywords:
            print("Word not included in supposed superset file: " + line)
