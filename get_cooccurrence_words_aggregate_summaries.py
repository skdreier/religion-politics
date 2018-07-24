import sys
import os

total_num_files = int(sys.argv[1])
output_name = sys.argv[2]
temp_results_dir = output_name + "-temp/"
results_dir = 'script_output/'
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)


def aggregate_all_files(total_num_processed_files):
    all_foundwords = []
    f = open(results_dir + output_name + "-cooccurrencecounts.csv", "w")
    f.write("searchword,foundword,foundwordcount,numwordsinsearchwordsnippets\n")
    searchword_foundword_dict = {}
    searchword_matchcount_dict = {}
    for i in range(total_num_processed_files):
        already_added_searchwordcount = False
        with open(temp_results_dir + "temp" + str(i) + ".txt", "r") as smallf:
            for line in smallf:
                four_pieces = line.strip().split('\t')
                searchword = four_pieces[0]
                foundword = four_pieces[1]
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
                if not already_added_searchwordcount:
                    try:
                        searchword_matchcount_dict[searchword] += searchwordcount
                    except:
                        searchword_matchcount_dict[searchword] = searchwordcount
                    already_added_searchwordcount = True
    for searchword in searchword_foundword_dict.keys():
        foundword_count_dict = searchword_foundword_dict[searchword]
        for foundword in foundword_count_dict.keys():
            count = foundword_count_dict[foundword]
            if foundword not in all_foundwords:
                all_foundwords.append(foundword)
            f.write(searchword + "," + foundword + "," + str(count) + "," +
                    str(searchword_matchcount_dict[searchword]) + "\n")
    f.close()
    with open("get_keyword_doc_counts_keywords_to_counts.txt", "w") as f:
        for foundword in all_foundwords:
            if '*' in foundword or '#' in foundword:
                continue
            f.write(foundword)
            f.write("\n")


def main():
    aggregate_all_files(total_num_files)


if __name__ == '__main__':
    main()
