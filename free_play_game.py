# free_play_game.py (código ajustado)

import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from services.word_generator import get_random_word
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
import winsound
import threading

# Importe as configurações do arquivo config.py
from config import (
    SoundPlayer,
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    ERROR_COLOR,
    FONT_SIZE,
    TYPING_COLOR,
    PADDING
)

class FreePlayGame:
    def __init__(self, root, switch_to_main_menu):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.sound_enabled = self.check_sound_support()
        self.listener = None
        self.typed_word = ""
        self.current_sentence = ""
        self.setup_ui()
        self.setup_keyboard_listener()
        
    def check_sound_support(self):
        try:
            winsound.Beep(1000, 10)
            return True
        except:
            return False

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.input_label = ttk.Label(
            self.main_frame,
            text="",
            font=("Helvetica", FONT_SIZE),
            wraplength=800,
            justify="center",
            foreground=TYPING_COLOR
        )
        self.input_label.pack(expand=True, pady=20)

        self.back_btn = ttk.Button(
            self.main_frame,
            text="← Voltar ao Menu",
            command=self.end_game,
            style="TButton"
        )
        self.back_btn.pack(pady=20, side=tk.BOTTOM)

    def setup_keyboard_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release, suppress=False)
        self.listener.start()

    def on_press(self, key):
        try:
            # Tenta obter o caractere da tecla.
            # Se for uma tecla normal (a, b, c, 1, 2, 3, etc.), 'key.char' terá um valor.
            char = key.char
            
            # Adiciona o caractere digitado à palavra atual
            if char is not None:
                self.typed_word += char
                # Reproduz o som da letra
                threading.Thread(target=lambda: play_audio(text_to_speech(char)), daemon=True).start()
        
        except AttributeError:
            # Se a tecla for especial (espaço, backspace, etc.), 'key.char' não existirá
            # e o código virá para este bloco.
            if key == keyboard.Key.space:
                # Se a palavra atual não estiver vazia, processa a palavra
                if self.typed_word:
                    # Roda a função de texto para fala em outra thread
                    threading.Thread(target=lambda: play_audio(text_to_speech(self.typed_word)), daemon=True).start()
                    
                    # Adiciona a palavra à frase e reinicia a palavra atual
                    self.current_sentence += self.typed_word + " "
                    self.typed_word = ""
            
            elif key == keyboard.Key.backspace:
                # Lógica para Backspace
                if self.typed_word:
                    self.typed_word = self.typed_word[:-1]
                elif self.current_sentence:
                    words = self.current_sentence.strip().split()
                    if words:
                        self.typed_word = words[-1]
                        self.current_sentence = " ".join(words[:-1]) + (" " if len(words) > 1 else "")
                threading.Thread(target=SoundPlayer.play_backspace, daemon=True).start()
            
            elif key == keyboard.Key.esc:
                self.end_game()
                return

        # Atualiza a interface em todas as situações para refletir a nova digitação
        self.update_ui()
    
    def on_release(self, key):
        pass

    def update_ui(self):
        display_text = self.current_sentence + self.typed_word
        self.input_label.config(text=display_text)

    def end_game(self):
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        self.main_frame.destroy()
        self.switch_to_main_menu()