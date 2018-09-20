total = 0

for i in range(100):
    print("Starting work on file " + str(i + 1))
    with open("allbuckets-aggregateddocfrequencies-nochecksum/docfrequenciespart" + str(i) + ".txt", "r") as f:
        for line in f:
            if line.strip() == '':
                continue
            line = line.strip()
            line = line[line.index(chr(1)) + 1:]
            num = int(line)
            total += num

print(total)
