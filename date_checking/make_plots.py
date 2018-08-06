import matplotlib.pyplot as plt
import seaborn as sns


year_x = []
year_y = []
year_distincty = []

month_x = []
month_y = []
month_distincty = []

day_x = []
day_y = []
day_distincty = []

with open('script_output/year-bins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        year = int(line[:line.index('\t')])
        count = int(line[line.index('\t') + 1:])
        year_x.append(year)
        year_y.append(count)
with open('script_output/year-distincturlbins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        count = int(line[line.index('\t') + 1:])
        year_distincty.append(count)


with open('script_output/month-bins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        month = line[:line.index('\t')]
        month = float(month[:4]) + ((float(month[4:]) - 1)/ 12)
        count = int(line[line.index('\t') + 1:])
        month_x.append(month)
        month_y.append(count)
with open('script_output/month-distincturlbins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        count = int(line[line.index('\t') + 1:])
        month_distincty.append(count)


with open('script_output/day-bins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        day = line[:line.index('\t')]
        day = float(day[:4]) + ((float(day[4:6]) - 1)/ 12) + ((float(day[6:]) - 1)/ (12 * 31))
        count = int(line[line.index('\t') + 1:])
        day_x.append(day)
        day_y.append(count)
with open('script_output/day-distincturlbins.txt', "r") as f:
    for line in f:
        line = line.strip()
        if line == '':
            continue
        count = int(line[line.index('\t') + 1:])
        day_distincty.append(count)


sns.set()
ax = plt.subplot(111)
ax.set_yscale('log')
plt.scatter(year_x, year_y, label="Total page captures in year")
plt.scatter(year_x, year_distincty, label="Total URLs with >=1 capture in year")
plt.xticks([i for i in range(1996, 2015)])
plt.legend()
plt.xlabel("Date")
plt.ylim(1, None)
plt.title("Page captures by year")
plt.show()


ax = plt.subplot(111)
ax.set_yscale('log')
plt.scatter(month_x, month_y, s=10, label="Total page captures in month")
plt.scatter(month_x, month_distincty, s=10, label="Total URLs with >=1 capture in month")
plt.xticks([i for i in range(1996, 2015)])
plt.legend()
plt.xlabel("Date")
plt.ylim(1, None)
plt.title("Page captures by month")
plt.show()


ax = plt.subplot(111)
ax.set_yscale('log')
plt.scatter(day_x, day_y, s=1.5, label="Total page captures in day", color='r')
plt.scatter(day_x, day_distincty, s=1.5, label="Total URLs with >=1 capture in day", color='g')
plt.xticks([i for i in range(1996, 2015)])
plt.legend()
plt.xlabel("Date")
plt.ylim(1, None)
plt.title("Page captures by day")
plt.show()
