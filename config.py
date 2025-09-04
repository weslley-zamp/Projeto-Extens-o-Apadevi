# config.py

import winsound
import threading

BACKGROUND_COLOR = "#2c3e50"
CORRECT_COLOR = "#27ae60"
ERROR_COLOR = "#e74c3c"
FONT_SIZE = 28
TYPING_COLOR = "#3498db"
PADDING = 30
WORDS_PER_GAME = 30

class SoundPlayer:
    _playing = False
    @classmethod
    def play_letter_correct(cls):
        if cls._playing: return
        try:
            cls._playing = True
            winsound.Beep(800, 100)
        except: print("\a")
        finally: cls._playing = False
    @classmethod
    def play_backspace(cls):
        if cls._playing: return
        try:
            cls._playing = True
            winsound.Beep(200, 100)
        except: print("\a")
        finally: cls._playing = False
    @classmethod
    def play_word_correct(cls):
        if cls._playing: return
        try:
            cls._playing = True
            winsound.Beep(1000, 200)
        except: print("\a\a")
        finally: cls._playing = False
    @classmethod
    def play_error(cls):
        if cls._playing: return
        try:
            cls._playing = True
            winsound.Beep(400, 300)
        except: print("\a\a")
        finally: cls._playing = False