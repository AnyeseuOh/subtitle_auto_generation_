from nltk.tokenize import word_tokenize
from nltk.tokenize.regexp import RegexpTokenizer
#-*-coding: utf-8-*-
import pymysql
import numpy as np;

fw=open("fortest_make.smi",'w',encoding='UTF8')
#smi파일 맨위 기본설정부
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
#translation=번역
#output1=시작시간
#output2=종료시간
#sportnew2=기존 번역문장(구두점코드 완성시 그거 output으로 변형 요망)
ftran=open("result.txt",'r',encoding='UTF8')
ftimestart=open("s_time.txt",'r',encoding='UTF8')
ftimeend=open("e_time.txt",'r',encoding='UTF8')
fs=open("txt_file.txt",'r',encoding='UTF8')
body="<BODY>\n"
index=0
timeindex=[]
lines=fs.readlines()
tokenizer = RegexpTokenizer("\s+", gaps=True)
#단어별로 쪼개서 몇번쨰에서 문장이 끝나는지 기록
#timeindex에 들어있음.
for i in range(len(lines)):
    token=tokenizer.tokenize(lines[i])
    index=index+len(token)
    timeindex.append(index)
st=ftimestart.readlines()
et=ftimeend.readlines()
tokenizer=RegexpTokenizer(",",gaps=True)
st=str(st)
et=str(et)
#시작시간 끝나는시간 단어별로 쪼개서 list에 저장
time_start=tokenizer.tokenize(st)
time_end=tokenizer.tokenize(et)
#확인용코드
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
        #확인용코드
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
        #확인용코드
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
    #smi파일에서는 초로만 계산해서 초로 바꾸는 부분
    start=start_second*1000+start_second2*10
    end=end_second*1000+end_second2*10
    #자막입력
    body=body+"<SYNC Start="+str(start)+">\n<P Class=KRCC>"+content[i]+"\n"
    body=body+"<SYNC Start="+str(end)+">\n<P Class=KRCC>&nbsp;</P>\n"

body=body+"</BODY>\n"
body=body+"</SAMI>"
fw.write(body)
fw.close()
