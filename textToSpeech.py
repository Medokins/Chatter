#this is mostly for fun while I wait for facebook to finally send data...
import os
import gtts
from playsound import playsound

def respond(text):
    tts = gtts.gTTS(text)
    tts.save(os.path.join("voice_samples", "sample.mp3"))
    playsound(os.path.join("voice_samples", "sample.mp3"))