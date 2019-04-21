from time import sleep
import os


dir_to_monitor = 'all_religious_word_contexts/'
total_threads_originally_used = 7
original_num_per_doc = 500
new_num_per_doc = 50000
assert original_num_per_doc % original_num_per_doc == 0, "Make new_num_per_doc divisible by original_num_per_doc"
if not dir_to_monitor.endswith('/'):
    dir_to_monitor += '/'


next_file_to_appear_for_a_condensing = [new_num_per_doc + 1] * total_threads_originally_used
num_to_add = original_num_per_doc - 1
string_is = [str(i) for i in range(total_threads_originally_used)]


def can_condense_files():
    for i in range(total_threads_originally_used):
        if os.path.isfile(dir_to_monitor + string_is[i] + '_' + str(next_file_to_appear_for_a_condensing[i]) + '-' +
                          str(next_file_to_appear_for_a_condensing[i] + num_to_add) + '.txt'):
            return True
    return False


while True:
    if can_condense_files():
        for i in range(total_threads_originally_used):
            if os.path.isfile(dir_to_monitor + string_is[i] + '_' + str(next_file_to_appear_for_a_condensing[i]) + 
                              '-' + str(next_file_to_appear_for_a_condensing[i] + num_to_add) + '.txt'):
                new_filename_end_num = next_file_to_appear_for_a_condensing[i] - 1
                new_filename_start_num = next_file_to_appear_for_a_condensing[i] - new_num_per_doc
                new_filename = dir_to_monitor + string_is[i] + '_' + str(new_filename_start_num) + '-' + \
                               str(new_filename_end_num) + '.txt'
                cur_mini_start_num = new_filename_start_num
                with open(new_filename, 'w') as f:
                    while cur_mini_start_num < new_filename_end_num + 1:
                        old_filename = dir_to_monitor + string_is[i] + '_' + str(cur_mini_start_num) + '-' + \
                                       str(cur_mini_start_num + num_to_add) + '.txt'
                        cur_mini_start_num += original_num_per_doc
                        with open(old_filename, 'r') as old_f:
                            for line in old_f:
                                f.write(line)
                        os.remove(old_filename)
                next_file_to_appear_for_a_condensing[i] = new_filename_end_num + new_num_per_doc + 1
    else:
        sleep(10)
