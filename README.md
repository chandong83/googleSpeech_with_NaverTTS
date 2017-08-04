# Google Speech API + Naver TTS
# 구글 음성 인식(Google Speech) API 서비스와 네이버 TTS(Clova Speech Synthesis:CSS)의 합체 코드


<pre>
필요한 패키지들은 다음과 같습니다.
sudo apt-get install python3-dev
sudo apt install portaudio19-dev
sudo pip3 install pyaudio
sudo pip3 install -r requirements.txt
#ubuntu
sudo apt-get install vlc

export GOOGLE_APPLICATION_CREDENTIALS=[api key 위치.json]
</pre>


## 변경이 필요한 부분.
~~~~~
file : naverTTS.py
//네이버 KEY
var client_id = '당신의 네이버 API ID';
var client_secret = '당신의 네이버 API 암호키';


def play(self, txt):
...
#외부 프로그램 사용 vlc
#os.system('cvlc ' + tmpPlayPath + ' --play-and-exit')
#라즈베리파이
os.system('omxplayer ' + tmpPlayPath)
~~~~~


~~~
file : googleSpeech_mic.py
cmdLists = [
        #명령어               대답                     종료 리턴값
        [u'끝내자',     '그럼 이만 물러가겠습니다.',            0],
        [u'안녕',       '안녕하십니까?',                      1],
        [u'누구냐',     '저는 구글 스피치와 네이버 TTS입니다.',   1],
        [u'이름이 뭐니', '저는 아슬리 입니다.',                 1],
        [u'나이는',     '저는 이제 태어났어요.',                1],
        [u'뭘 좋아해',   '다 좋아합니다.',                     1]]
~~~



##실행 방법
~~~
$python3 googleSpeech_mic.py
~~~


http://blog.naver.com/chandong83
