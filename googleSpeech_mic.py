# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START import_libraries]
from __future__ import division

import re
import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

import naverTTS

# [END import_libraries]

#네이버 TTS 클레스

# speaker
#
#  0 : 'mijin',     #한국어 여성
#  1 : 'jinho',     #한국어 남성
# speed
#     0 = 일반 속도
#tts = naverTTS.NaverTTS(0, 0)
#or
tts = naverTTS.NaverTTS()


#명령어 처리
cmdLists = [
        #명령어               대답                     종료 리턴값
        [u'끝내자',     '그럼 이만 물러가겠습니다.',            0],
        [u'안녕',       '안녕하십니까?',                      1],
        [u'누구냐',     '저는 구글 스피치와 네이버 TTS입니다.',   1],
        [u'이름이 뭐니', '저는 아슬리 입니다.',                 1],
        [u'나이는',     '저는 이제 태어났어요.',                1],
        [u'뭘 좋아해',   '다 좋아합니다.',                     1]]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self.isPause = False

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()


        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return

            if self.isPause:
                continue

            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    #일시 정지
    def pause(self):
        self.isPause = True

    #재 시작
    def restart(self):
        self.isPause = False
# [END audio_stream]


"""
리턴이 1이면 종료
"""
def CommandProc(stt):
    # 문자 양쪽 공백 제거
    cmd = stt.strip()
    # 입력 받은 문자 화면에 표시
    # 2.x
    #print('나 : ' + cmd.encode('utf-8'))
    # 3.x
    print('나 : ' + str(cmd))

    # 2.x : 문자가 unicode인지 확인 필요
    # if type(cmd) is unicode:

    #명령 리스트와 비교
    for cmdList in cmdLists:
        # 같은 유니코드끼린 바로 대입이 가능하다.
        if str(cmd) == cmdList[0]:

            #네이버 TTS
            tts.play(cmdList[1])

            #구글 스피치 대답 화면에 표시
            print ('구글 스피치 : ' + cmdList[1])

            # 종료 명령 리턴 0이면 종료
            # 1이면 계속
            return cmdList[2]

    # 명령이 없거나
    # unicode가 아니면 못 알아 들었다고 화면에 표시하고
    # 계속
    print ("죄송합니다. 알아듣지 못했습니다.")

    tts.play("죄송합니다. 알아듣지 못했습니다.")
    return 1


def listen_print_loop(responses, mic):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # There could be multiple results in each response.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            #### 추가 ### 화면에 인식 되는 동안 표시되는 부분.
            sys.stdout.write('나 : ')
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            # 에코 방지용
            #마이크 일시 중지
            mic.pause()

            if CommandProc(transcript) == 0:
                break;

            #마이크 재 시작
            mic.restart()
            """
                # 원래 있던 코드는 주석처리
                print(transcript + overwrite_chars)
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break
            """
            num_chars_printed = 0


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    #language_code = 'en-US'  # a BCP-47 language tag
    language_code = 'ko-KR'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses, stream)


if __name__ == '__main__':
    main()
