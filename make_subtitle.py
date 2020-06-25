from __future__ import print_function
import time
import boto3
import json
import requests
import os
import sys
import urllib.request
import sys
from nltk.tokenize import word_tokenize
from nltk.tokenize.regexp import RegexpTokenizer
#-*-coding: utf-8-*-
import pymysql
import numpy as np;
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import subprocess
class testDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(testDialog, self).__init__(parent)
 
        form = QtGui.QFormLayout()
        form.setHorizontalSpacing(0)

        position="asd"
        self.myedit = QtGui.QLineEdit()
        self.myedit.setDragEnabled(True)
        self.myedit.setAcceptDrops(True)
        self.myedit.installEventFilter(self)
 
        form.addWidget(self.myedit)
 
        self.setLayout(form)
        self.setGeometry(300, 300, 400, 150)
        self.setWindowTitle('make smi file')

        self.label=QLabel("파일: ",self)
        self.label.move(20,50)
        self.label.resize(300,20)

        findButton=QPushButton("file select",self)
        findButton.move(300,50)
        findButton.clicked.connect(self.findButton_clicked)

        pybutton=QPushButton("make file",self)
        pybutton.resize(100,32)
        pybutton.move(150,100)
        #pybutton.clicked.connect(QCoreApplication.instance().quit)
        pybutton.clicked.connect(self.close)
 
    @QtCore.pyqtSlot(str)   # int represent the column value

    def findButton_clicked(self):
        fname=QFileDialog.getOpenFileName(self)
        self.label.setText(fname)
        
    def clickAction(self):
        print("click")
    
    def eventFilter(self, object, event):
        if (object is self.myedit):
            if (event.type() == QtCore.QEvent.DragEnter):
                if event.mimeData().hasUrls():
                    event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
                    print ("accept")
                else:
                    event.ignore()
                    print ("ignore")
            if (event.type() == QtCore.QEvent.Drop):
                if event.mimeData().hasUrls():   # if file or link is dropped
                    urlcount = len(event.mimeData().urls())  # count number of drops
                    url = event.mimeData().urls()[0]   # get first url
                    self.label.setText(url.toLocalFile())
                    #event.accept()  # doesnt appear to be needed
            return False # lets the event continue to the edit
        return False

class completeDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(completeDialog, self).__init__(parent)
 
        form = QtGui.QFormLayout()
        form.setHorizontalSpacing(0)
 
        self.setLayout(form)
        self.setGeometry(300, 300, 400, 80)
        self.setWindowTitle('complete')

        pybutton=QPushButton("end program",self)
        pybutton.resize(100,32)
        pybutton.move(150,20)
        #pybutton.clicked.connect(QCoreApplication.instance().quit)
        pybutton.clicked.connect(self.close)
 
    @QtCore.pyqtSlot(str)   # int represent the column value
        
    def clickAction(self):
        print("click")   


 
app = QtGui.QApplication([])
dl = testDialog()
dl.exec_()
position=dl.label.text()
position=position.replace("\\","/")
command = "ffmpeg -i "
command=command+position+" -ab 160k -ac 2 -ar 44100 -vn audio.wav"
subprocess.call(command, shell=True)

#################### Voice to Text + find. + Timestamp ####################


s3 = boto3.client('s3')
file_start = open('s_time.txt','w')
file_end = open('e_time.txt','w')
file02 = open('txt_file.txt','w')
filename = "audio.wav"
job_name = "timestampto"
#bucket name


s3.upload_file(filename, job_name, filename)
#s3 upload

job_name1 = "timestamp_test2"
#name should be changed


transcribe = boto3.client('client', region_name = 'region_name')
job_uri = "job_uri/"+filename
#stored file s3 address

transcribe.start_transcription_job(
    TranscriptionJobName=job_name1,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US',
    Settings={'ChannelIdentification': True}
)

print("{0}:  Started job {1} …".format(time.ctime(), job_name1))

while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name1)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("{0}:  Still going ({1}) … ".format(time.ctime(), status['TranscriptionJob']['TranscriptionJobStatus']))
    time.sleep(30)

print("{0}:  It’s done ({1}).".format(time.ctime(), status['TranscriptionJob']['TranscriptionJobStatus']))


# if we completed successfully, then get the full text of the transcript

if (status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED'):
    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    # get the transcript JSON
    transcript = json.loads((requests.get(transcript_uri)).text)
    print("Transcript:")
    # we could check the number_of_channels to be sure, but we’ll just assume two channels for this example
    # get the left channel transcript as a blob of text

    s_time = []
    e_time = []
    txt = ""
            
    for item in transcript['results']['channel_labels']['channels'][0]["items"]:
        if (item['type'] == "pronunciation"):
            s_time.append(item['start_time'])
            e_time.append(item['end_time'])
            txt += item['alternatives'][0]['content']
            txt += " "
        elif (item['type'] == "punctuation"):
            txt += item['alternatives'][0]['content']
            txt += " "




    # get the right channel transcript as a blob of text
    #print(get_transcript_text(transcript['results']['channel_labels']['channels'][1]["items"]))

else:
    print("Job status is {0}".format(status['TranscriptionJob']['TranscriptionJobStatus']))


print("start time is ", s_time, "\n")
print("end time is ", e_time)

for i in s_time:
    file_start.write(i)
    file_start.write(",")


for i in e_time:
    file_end.write(i)
    file_end.write(",")


txt = txt.replace(" ,",",")
txt = txt.replace(" .",".\n")
txt = txt.replace(" !","!\n")
txt = txt.replace(" ?","?\n")

for i in txt:
    file02.write(i)


file_start.close()
file_end.close()
file02.close()


#################### translate ####################

f=open("txt_file.txt","r")
encText = urllib.parse.quote(f.read())
f.close()

# translate and save text file

client_id = "cliendt_id"
client_secret = "client_secret"

f2=open("result.txt","w",encoding='UTF8')

print("Start translating ")


data = "source=en&target=ko&text=" + encText

url = "https://openapi.naver.com/v1/papago/n2mt"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()


if(rescode==200):
    response_body = response.read()
    txt = "" + response_body.decode('utf-8')
    txt = txt[152:-4]
    
    txt = txt.replace(".",".\n")
    txt = txt.replace("!","!\n")
    txt = txt.replace("?","?\n")
            
    f2.write(txt)
    print("Translated text file is saved.")
else:
    print("Error Code:" + rescode)


f2.close()

#sql db connect
conn=pymysql.connect(host='localhost',user='root',password='12345',db='dictionary',charset='utf8')
curs=conn.cursor()
curs.execute("set names utf8")
#wrong text exchange
ftran=open("c:/translation.txt",'r',encoding='UTF8')
lines=ftran.readlines()
tokenizer = RegexpTokenizer("\s+", gaps=True)
writebuffer=[]
for i in range(len(lines)):
    token=tokenizer.tokenize(lines[i])
    if token[0]=="#":
        word=token.remove("#")
        word=lower(word)
        sql="select description from engkor where word ="+word
        curs.execute(sql)
        rows=curs.fetchone()
        #python korean languge problem->incoding, decoding
        row=row.encode('ISO-8859-1')
        row=row.decode('euc-kr')
        tokenizer2 = RegexpTokenizer("'FONT'", gaps=True)
        token2=tokenizer2(row)
        i=15;
        new=token2[i]
        for j in range(len(token2)-17):
            i=i+1
            new=new+token2[i]
        token=new;
    writebuffer.append(token)
ftran.close()
#insert to file
ftran=open("c:/data/translation.txt",'w',encoding='UTF8')
for i in range(len(writebuffer)):
    for j in range(len(writebuffer[i])):
        ftran.write(writebuffer[i][j]+" ")
    ftran.write("\n")
ftran.close()

#make smi file
fw=open("subtitle.smi",'w',encoding='UTF8')
#smi file default setup
init="<SAMI>\n"
init=init+"<HEAD>\n"
init=init+"<STYLE TYPE=”text/css>\n"
init=init+"<!—->\n"
init=init+"P{margin-left:8pt;\n"
init=init+"margin-right:8pt;margin-bottom:2pt;\n"
init=init+"Margin-top:2pt; font-size:20pt;\n"
init=init+"text-align:center;\n"
init=init+"Font-family:굴림, Arial;\n"
init=init+"font-weight:bold; color:white;\n"
init=init+"Background-color:black;}\n"
#init=init+".KRCC{Name:한국어; lang:kr-KR; SAMIType:CC;\n}"
#init=init+".ENCC{name:English; lang:en-US; SAMIType:CC;\n}"
#init=init+"-->\n"
init=init+"</STYLE>\n"
init=init+"</HEAD>\n"
fw.write(init)
#translation=translate
#output1=start time
#output2=end time
ftran=open("result.txt",'r',encoding='UTF8')
ftimestart=open("s_time.txt",'r',encoding='UTF8')
ftimeend=open("e_time.txt",'r',encoding='UTF8')
fs=open("txt_file.txt",'r',encoding='UTF8')
body="<BODY>\n"
index=0
timeindex=[]
lines=fs.readlines()
tokenizer = RegexpTokenizer("\s+", gaps=True)
#divide by word and record where the sentence is ended
#timeindex has that information
for i in range(len(lines)):
    token=tokenizer.tokenize(lines[i])
    index=index+len(token)
    timeindex.append(index)
st=ftimestart.readlines()
et=ftimeend.readlines()
tokenizer=RegexpTokenizer(",",gaps=True)
st=str(st)
et=str(et)
#word's start time and end time record
time_start=tokenizer.tokenize(st)
time_end=tokenizer.tokenize(et)
#confirm code
print(time_start)
print(time_end)
content=ftran.readlines()
print(len(content))
print(len(lines))
#print(content)
tokenizer=RegexpTokenizer(",",gaps=True)
#content=str(content)
#content=tokenizer.tokenize(content)
#for i in range(len(content)):
 #   print(content[i])
for i in range(len(content)):
    if i==0:
        time=time_start[0]
        #confirm code
        print("time :",time)
    else:
        time=time_start[timeindex[i-1]+1]
        print(i)
        print(timeindex[i])
        print("time :",time)
    second=time.split(".")
    second[0]=second[0].replace("[","")
    second[0]=second[0].replace("'","")
    second[0]=second[0].replace("]","")
    print(second[0])
    print(second[1])
    start_second=int(second[0])
    start_second2=int(second[1])    
    if i==0:
        time=timeindex[0]
        time=time_end[time-1]
        #confirm code
        print("time :",time)
    else:
        time=time_end[timeindex[i]]
        print(i)
        print(timeindex[i])
        print("time :",time)
    if i==len(content)-1:
        time=time_end[timeindex[i-1]]
    second=time.split(".")
    second[0]=second[0].replace("[","")
    second[0]=second[0].replace("'","")
    second[0]=second[0].replace("]","")
    end_second=int(second[0])
    end_second2=int(second[1])
    #smi file compute by second-> compile it to second
    start=start_second*1000+start_second2*10
    end=end_second*1000+end_second2*10
    #insert subtitle
    body=body+"<SYNC Start="+str(start)+">\n<P Class=KRCC>"+content[i]+"\n"
    body=body+"<SYNC Start="+str(end)+">\n<P Class=KRCC>&nbsp;</P>\n"

body=body+"</BODY>\n"
body=body+"</SAMI>"
fw.write(body)
fw.close()

complete=completeDialog()
complete.exec_()
sys.exit(app.exec_())
#sys.exit(app.closeAllWindows())


