
# -*- coding: utf-8 -*-
# 네이버 음성합성 Open API 예제
import os
import sys
import urllib.request

client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
client_id = "J98NrWEQXQ_1wZnGmPQw"
client_secret = "5XNMPh0LYT"

url = "https://openapi.naver.com/v1/voice/tts.bin"

speakers = [
    'mijin',     #한국어 여성
    'jinho',     #한국어 남성
    'clara',     #영어 여성
    'matt',      #영어 남성
    'yuri',      #일본어 여성
    'shinji',    #일본어 남성
    'meimei',    #중국어 여성
    'liangliang',#중국어 남성
    'jose',      #스페인어 남성
    'carmen'     #스페인어 여성
    ]


tmpPlayPath = './tmp.mp3'

class NaverTTS():
    def __init__(self, speaker=0, speed=0):
        self.speaker = speakers[speaker]
        self.speed=str(speed)
    def play(self, txt):
        encText = urllib.parse.quote(txt)
        data = "speaker=" + self.speaker + "&speed=" + self.speed + "&text=" + encText;

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request, data=data.encode('utf-8'))
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            with open(tmpPlayPath, 'wb') as f:
                f.write(response_body)

            #외부 프로그램 사용 vlc
            os.system('cvlc ' + tmpPlayPath + ' --play-and-exit')
            #라즈베리파이
            #os.system('omxplayer ' + tmpPlayPath)
        else:
            print("Error Code:" + rescode)


def main():
    tts = NaverTTS()
    tts.play("안녕하십니까?")

if __name__ == '__main__':
    main()
