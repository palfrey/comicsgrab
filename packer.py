from sys import argv
from os import listdir, system
from os.path import exists

folder = argv[1]

years = []

for f in sorted(listdir(folder)):
	year = int(f[:4])
	if year not in years:
		years.append(year)

print(years)

for year in years:
	fname = "%s-%s.cbz"%(folder, year)
	if not exists(fname):
		cmd = "zip %s %s/%s*"%(fname,folder, year)
		print(cmd)
		system(cmd)
