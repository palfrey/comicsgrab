# Copyright (C) 2010  Alex Yatskov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import image
import sys

target = "output"

if not os.path.exists(target):
	os.mkdir(target)

root = sys.argv[1]
for folder in os.listdir(root):
	sourceFolder = os.path.join(root,folder)
	if not os.path.isdir(sourceFolder):
		continue
	targetFolder = os.path.join(target, folder)
	if not os.path.exists(targetFolder):
		os.mkdir(targetFolder)
	print(targetFolder)
	for (idx,f) in enumerate(sorted(os.listdir(sourceFolder))):
		sf = os.path.join(sourceFolder, f)
		tfName = "%02d-%s.png"%(idx,os.path.splitext(f)[0])
		if idx == 0:
			mangaName = os.path.join(targetFolder, folder+'.manga')
			manga = open(mangaName, 'w')
			manga.write('\x00')
			manga.close()

			mangaSaveName = os.path.join(targetFolder, folder+'.manga_save')
			mangaSave = open(mangaSaveName, 'w')
			saveData = 'LAST=/mnt/us/pictures/%s/%s' % (folder, tfName)
			mangaSave.write(saveData.encode('utf-8'))
			mangaSave.close()
		tf = os.path.join(targetFolder, tfName)
		print(tf)
		if not os.path.isfile(tf):
			image.convertImage(sf, tf, "Kindle 3", image.ImageFlags.Orient | image.ImageFlags.Resize | image.ImageFlags.Frame | image.ImageFlags.Quantize)
