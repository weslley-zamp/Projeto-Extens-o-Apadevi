from gtts import gTTS
from io import BytesIO

def text_to_speech(text):
    mp3_fp = BytesIO()
    tts = gTTS(text=text, lang='pt-br')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp
