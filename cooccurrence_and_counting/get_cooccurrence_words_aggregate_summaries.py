import sys
import os

total_num_files = int(sys.argv[1])
output_name = sys.argv[2]
temp_results_dir = output_name + "-temp/"
results_dir = 'script_output/'
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)


def get_stop_words_dict():
    stop_words_dict = {}
    with open("stop_words.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line != '':
                stop_words_dict[line] = True
    return stop_words_dict


def aggregate_all_files(total_num_processed_files):
    all_foundwords = []
    stop_words_dict = get_stop_words_dict()
    f = open(results_dir + output_name + "-cooccurrencecounts.csv", "w")
    f.write("searchword,foundword,foundwordcount,numwordsinsearchwordsnippets\n")
    searchword_foundword_dict = {}
    searchword_matchcount_dict = {}
    for i in range(total_num_processed_files):
        with open(temp_results_dir + "temp" + str(i) + ".txt", "r") as smallf:
            for line in smallf:
                four_pieces = line.strip().split('\t')
                searchword = four_pieces[0]
                foundword = four_pieces[1]
                if stop_words_dict.get(foundword, False):
                    continue
                count = int(four_pieces[2])
                searchwordcount = int(four_pieces[3])
                try:
                    foundword_count_dict = searchword_foundword_dict[searchword]
                    try:
                        foundword_count_dict[foundword] += count
                    except:
                        foundword_count_dict[foundword] = count
                except:
                    searchword_foundword_dict[searchword] = {foundword: count}
                searchword_matchcount_dict[searchword] = searchwordcount
    for searchword in searchword_foundword_dict.keys():
        foundword_count_dict = searchword_foundword_dict[searchword]
        for foundword in foundword_count_dict.keys():
            count = foundword_count_dict[foundword]
            if foundword not in all_foundwords:
                all_foundwords.append(foundword)
            f.write(searchword + "," + foundword + "," + str(count) + "," +
                    str(searchword_matchcount_dict[searchword]) + "\n")
    f.close()
    with open("get_keyword_doc_counts_keywords_to_count.txt", "w") as f:
        words_with_nonalpha = []
        only_alpha_words = []
        for foundword in all_foundwords:
            if '*' in foundword or '#' in foundword:
                continue
            whole_foundword_is_letters = True
            for letter in foundword:
                if not letter.isalpha():
                    whole_foundword_is_letters = False
            if whole_foundword_is_letters:
                only_alpha_words.append(foundword)
            else:
                words_with_nonalpha.append(foundword)
        words_with_nonalpha = sorted(words_with_nonalpha, key=(lambda x: len(x)), reverse=True)
        only_alpha_words = sorted(only_alpha_words, key=(lambda x: len(x)), reverse=False)
        for foundword in words_with_nonalpha:
            f.write(foundword)
            f.write("\n")
        for foundword in only_alpha_words:
            f.write(foundword)
            f.write("\n")


def main():
    aggregate_all_files(total_num_files)


if __name__ == '__main__':
    main()
