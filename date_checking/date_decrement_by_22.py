# days returned by day_binner.pig are all shifted up by 22; shift them back down.

for dir_name in ['day-bins/', 'day-distincturlbins/']:
    for i in range(100):
        if i < 10:
            filename = dir_name + "part-r-0000" + str(i) + ".txt"
        else:
            filename = dir_name + "part-r-000" + str(i) + ".txt"
        lines = []
        with open(filename, "r") as f:
            for line in f:
                if line.strip() != '':
                    lines.append(line)
        with open(filename, "w") as f:
            for line in lines:
                int_date = int(line[:line.index('\t')]) - 22
                f.write(str(int_date) + line[line.index('\t'):])

