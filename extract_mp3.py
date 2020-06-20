import os
import subprocess
import pytube
import glob

yt = pytube.YouTube("Youtube_link")
vids = yt.streams.all()

for i in range(len(vids)):
    print(i,'.',vids[i])


vnum = 0
parent_dir = "Path_to_download___mp3"
vids[vnum].download(parent_dir)

default_filename=vids[vnum].default_filename
files = glob.glob(default_filename)
for x in files:
    if not os.path.isdir(x):
        filename = os.path.splitext(x)
        try:
            os.rename(x, filename[0] + '.mp3')
        except:
            pass

print('동영상 다운로드 및 mp3 변환 완료')
