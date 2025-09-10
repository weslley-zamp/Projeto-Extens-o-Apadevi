# free_mode.py

import tkinter as tk
from tkinter import ttk
import keyboard
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
import threading

# Importa as configurações
from config import CONFIG, contrast_text_color

class FreeModeGame:
    def __init__(self, root, switch_to_main_menu):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.typed_text = ""
        self.accent_char = None  # Novo atributo para armazenar o acento
        
        self.root.focus_force() 
        
        # Sempre pega a configuração atualizada
        self.bg_color = CONFIG["BACKGROUND_COLOR"]
        self.fg_color = CONFIG["FOREGROUND_COLOR"]
        self.font_size = CONFIG["FONT_SIZE"]
        self.padding = CONFIG["PADDING"]

        self.setup_ui()
        self.setup_keyboard_hook()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", self.font_size), background=self.bg_color)
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, padx=self.padding, pady=self.padding)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        self.text_label = ttk.Label(
            self.main_frame,
            text="Comece a digitar...",
            font=("Helvetica", 24),
            foreground=self.fg_color,
            background=self.bg_color
        )
        self.text_label.pack(pady=20, expand=True)

        self.back_btn = ttk.Button(
            self.main_frame,
            text="← Voltar ao Menu",
            command=self.end_game,
            style="TButton"
        )
        self.back_btn.pack(pady=20)
    
    def setup_keyboard_hook(self):
        keyboard.on_press(self.on_press_event)

    def on_press_event(self, event):
        # Lida com teclas especiais como backspace e esc
        if event.name == 'backspace':
            self.typed_text = self.typed_text[:-1]
            self.accent_char = None  # Limpa o acento se a tecla for backspace
            self.update_ui()
            return
        elif event.name == 'esc':
            self.end_game()
            return
        elif event.name == 'space':
            last_word = self.typed_text.split()[-1] if self.typed_text else ""
            if last_word:
                threading.Thread(
                    target=lambda: play_audio(text_to_speech(last_word)),
                    daemon=True
                ).start()
            self.typed_text += " "
            self.accent_char = None
            self.update_ui()
            return
            
        # Dicionário de acentos e suas combinações
        accent_map = {
            '`': 'aáeéiíoóuú',
            '´': 'aáeéiíoóuú',
            '~': 'aãeẽiĩoõuũ',
            '^': 'aâeêiîoôuû',
            '¨': 'aäeëiïoöuü'
        }

        # Verifica se a tecla pressionada é um acento
        if event.name in accent_map.keys():
            self.accent_char = event.name
            return

        # Lida com caracteres de texto, incluindo acentos
        if event.name and len(event.name) == 1:
            char = event.name.lower()
            
            if self.accent_char:
                if char in accent_map[self.accent_char]:
                    if self.accent_char == '´':
                        char = 'áéíóú'['aeiou'.find(char)]
                    elif self.accent_char == '~':
                        char = 'ãẽĩõũ'['aeiou'.find(char)]
                    
                    self.typed_text += char
                    threading.Thread(
                        target=lambda: play_audio(text_to_speech(char)),
                        daemon=True
                    ).start()
                else:
                    self.typed_text += self.accent_char
                    self.typed_text += char
                    threading.Thread(
                        target=lambda: play_audio(text_to_speech(self.accent_char + ' ' + char)),
                        daemon=True
                    ).start()
                
                self.accent_char = None
            else:
                self.typed_text += char
                threading.Thread(
                    target=lambda: play_audio(text_to_speech(char)),
                    daemon=True
                ).start()

            self.update_ui()

    def update_ui(self):
        self.text_label.config(
            text=self.typed_text,
            foreground=self.fg_color,
            background=self.bg_color
        )
    
    def end_game(self):
        keyboard.unhook_all()
        self.main_frame.destroy()
        self.switch_to_main_menu()
