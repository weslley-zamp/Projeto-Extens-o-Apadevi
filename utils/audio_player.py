from pygame import mixer

def play_audio(audio_bytesio):
    mixer.init()
    mixer.music.load(audio_bytesio, 'mp3')  # Carrega diretamente do BytesIO
    mixer.music.play()
    while mixer.music.get_busy():
        pass
