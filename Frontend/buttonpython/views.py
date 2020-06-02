from django.shortcuts import render
#import requests
import speech_recognition as sr 
from gtts import gTTS
import pygame
from io import BytesIO
import time
import sys
from django.http import HttpResponse
import time
import os
sys.path.append('..')
from run import run_application


def run(request):
    with BytesIO() as f:
        gTTS(request, lang='en').write_to_fp(f)
        f.seek(0)
        pygame.mixer.init()
        pygame.mixer.music.load(f)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

def button(request):
    #run("MY NAME IS SAIKUMAR I AM FROM NORTHEASTERN UNIVERSITY").delay()
    response = LogSuccessResponse(render(request,'home.html'))
    return response
    #return render(request,'home.html')

def aboutus(request):
    return render(request, 'aboutus.html')

class LogSuccessResponse(HttpResponse):

    def close(self):
        super(LogSuccessResponse, self).close()
        # import pdb
        # pdb.set_trace()
        # do whatever you want, this is the last codepoint in request handling
        time.sleep(5)
        run_application()
        print('HttpResponse successful: %s' % self.status_code)

# def output(request):
#     r = sr.Recognizer()
#
#     with sr.Microphone() as source:
#         print('Speak Something: ')
#         audio = r.listen(source)
#
#         try:
#             text = r.recognize_google(audio)
#             print('You said: {}'.format(text))
#         except:
#             print('Sorry could not recognize your voice')
#     return render(request, 'home.html',{'text':text})