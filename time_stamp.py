from __future__ import print_function
import time
import boto3
import json
import requests
import os
import sys
import urllib.request


#################### Voice to Text + 구두점 + Timestamp ####################


s3 = boto3.client('s3')
file_start = open('s_time.txt','w')
file_end = open('e_time.txt','w')
file02 = open('txt_file.txt','w')
filename = "How.wav"
job_name = "timestampto"
#버킷 이름


s3.upload_file(filename, job_name, filename)
#s3에 업로드

job_name1 = "timestamp01"
#같은 이름으로 진행시 오류남 / 따라서 새로운 파일을 진행할 때마다 job_name1은 달라져야함


transcribe = boto3.client('transcribe', region_name = 'ap-northeast-2')
job_uri = "https://timestampto.s3.ap-northeast-2.amazonaws.com/"+filename
#저장된 파일의 s3주소

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
txt = txt.replace(" .",".")
txt = txt.replace(" !","!")
txt = txt.replace(" ?","?")

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

client_id = "your_own_client_id"
client_secret = "your_own_client_secret"

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
