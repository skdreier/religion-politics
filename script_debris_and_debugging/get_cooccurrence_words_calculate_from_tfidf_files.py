import sys
import os


results_dir = 'script_output/'
assert os.path.isdir(results_dir), results_dir + " is supposed to already contain both the tf and idf info files"
idf_filename = results_dir + sys.argv[1]
tf_filename = results_dir + sys.argv[2]
output_filename = results_dir + sys.argv[3] + "-cooccurrencescores.csv"
num_words_to_take = int(sys.argv[4])

num_to_add_to_doc_frequency_for_each_foundword = 100

# fields in tf doc:
# searchword, foundword, foundwordcount, numwordsinsearchwordsnippets

# fields in idf doc (bear in mind that numcorpusdocsfoundwordappearsin only counts within this bucket):
# foundword, numcorpusdocsfoundwordappearsin

with open(output_filename, "w") as f:
    f.write("FoundWord,Score,NumFoundWordOccurrencesInAllSearchWordSnippets," +
            "TotalNumWordsInSearchWordSnippets,NumActualDocsFoundWordOccursIn," +
            "SpecificSearchWordSnippetOccurrences\n")


foundword_searchwordnumoccurrences_dict = {}
searchword_totalnumsnippetwords_dict = {}
searchword_foundwords_dict = {}
foundword_numactualdocs_dict = {}
foundword_totalsnippetoccurrences_dict = {}


with open(tf_filename, "r") as f:
    f.readline()  # get the header out of the way
    for line in f:
        if line.strip() == '':
            continue
        line = line.strip().split(',')
        searchword = line[0]
        foundword = line[1]
        foundwordcount = int(line[2])
        numwordsinsearchwordsnippets = int(line[3])
        try:
            if foundword not in searchword_foundwords_dict[searchword]:
                searchword_foundwords_dict[searchword].append(foundword)
        except:
            searchword_foundwords_dict[searchword] = [foundword]
        try:
            if searchword not in foundword_searchwordnumoccurrences_dict[foundword][0]:
                foundword_searchwordnumoccurrences_dict[foundword][0].append(searchword)
                foundword_searchwordnumoccurrences_dict[foundword][1].append(foundwordcount)
        except:
            foundword_searchwordnumoccurrences_dict[foundword] = [[searchword], [foundwordcount]]
        try:
            foundword_totalsnippetoccurrences_dict[foundword] += foundwordcount
        except:
            foundword_totalsnippetoccurrences_dict[foundword] = foundwordcount
        searchword_totalnumsnippetwords_dict[searchword] = numwordsinsearchwordsnippets


with open(idf_filename, "r") as f:
    f.readline()  # get the header out of the way
    for line in f:
        if line.strip() == '':
            continue
        line = line.strip().split(',')
        foundword = line[0]
        numactualdocs = int(line[1]) + num_to_add_to_doc_frequency_for_each_foundword
        foundword_numactualdocs_dict[foundword] = numactualdocs


searchword_foundwordscorelist_dict = {}
for searchword in searchword_foundwords_dict.keys():
    associated_foundwords = searchword_foundwords_dict[searchword]
    for foundword in associated_foundwords:
        searchword_ind = foundword_searchwordnumoccurrences_dict[foundword][0].index(searchword)
        tf = float(foundword_searchwordnumoccurrences_dict[foundword][1][searchword_ind] /
                             searchword_totalnumsnippetwords_dict[searchword])
        idf_denominator = float(foundword_numactualdocs_dict.get(foundword,
                                                                 num_to_add_to_doc_frequency_for_each_foundword + 1)
                                + len(foundword_searchwordnumoccurrences_dict[foundword][0]))
        score = tf / idf_denominator
        try:
            searchword_foundwordscorelist_dict[searchword].append((foundword, score))
        except:
            searchword_foundwordscorelist_dict[searchword] = [(foundword, score)]


foundword_score_list = []
for foundword in foundword_searchwordnumoccurrences_dict.keys():
    idf_denominator = float(foundword_numactualdocs_dict.get(foundword,
                                                             num_to_add_to_doc_frequency_for_each_foundword + 1) + 1)
    tf_numerator = float(sum(foundword_searchwordnumoccurrences_dict[foundword][1]))
    score = tf_numerator / idf_denominator
    foundword_score_list.append((foundword, score))


foundword_score_list = sorted(foundword_score_list, key=(lambda x: x[1]), reverse=True)[:num_words_to_take]

searchword_foundword_score_list = []
for searchword in searchword_foundwordscorelist_dict.keys():
    foundword_list = searchword_foundwordscorelist_dict[searchword]
    foundword_list = sorted(foundword_list, key=(lambda x: x[1]), reverse=True)[:num_words_to_take]
    searchword_foundwordscorelist_dict[searchword] = foundword_list
    for fw_score in foundword_list:
        searchword_foundword_score_list.append((searchword, fw_score[0], fw_score[1]))

searchword_foundword_score_list = \
    sorted(searchword_foundword_score_list, key=(lambda x: x[2]), reverse=True)


total_num_words_in_all_search_word_snippets = 0
for searchword in searchword_totalnumsnippetwords_dict:
    total_num_words_in_all_search_word_snippets += searchword_totalnumsnippetwords_dict[searchword]


with open(output_filename, "a") as f:
    for fw_score in foundword_score_list:
        foundword = fw_score[0]
        searchwords_snippet_counts = foundword_searchwordnumoccurrences_dict[foundword]
        searchwords = searchwords_snippet_counts[0]
        snippet_counts = searchwords_snippet_counts[1]
        searchword_str = ''
        for i in range(len(searchwords)):
            searchword_str += " " + searchwords[i].replace(",", "_comma_")
            searchword_str += " " + str(snippet_counts[i])
        if len(searchword_str) > 0:
            searchword_str = searchword_str[1:]
        f.write(foundword + "," + str(fw_score[1]) + "," +
                str(foundword_totalsnippetoccurrences_dict[foundword]) + "," +
                str(total_num_words_in_all_search_word_snippets) + "," +
                str(foundword_numactualdocs_dict.get(foundword, num_to_add_to_doc_frequency_for_each_foundword + 1) -
                    num_to_add_to_doc_frequency_for_each_foundword) + "," + searchword_str + "\n")
