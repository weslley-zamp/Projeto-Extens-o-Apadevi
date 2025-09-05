# main.py

import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from datetime import datetime
import sys
import os
import threading

# Importa as classes de jogo
from typing_game import TypingGame
from free_mode import FreeModeGame

# Importa as configurações do novo arquivo
from config import (
    BACKGROUND_COLOR,
    FONT_SIZE,
    PADDING
)
from services.tts_service import text_to_speech
from utils.audio_player import play_audio


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.current_game_instance = None
        self.listener = None
        self.current_selection = 0  # 0: Modo Padrão, 1: Modo Livre
        self.level_selection = 0  # 0: Fácil, 1: Médio, 2: Difícil, 3: Voltar
        self.menu_options = ["Modo Jogo Padrão", "Modo Jogo Livre"]
        self.level_options = ["Fácil", "Médio", "Difícil", "Voltar"]
        self.current_frame = None  # Para rastrear o frame atual
        self.setup_window()
        self.setup_keyboard_listener()
        self.show_main_menu()
        self.announce_menu_options()

    def setup_window(self):
        self.root.title("KeyEarn")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.geometry("1080x720")
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def setup_keyboard_listener(self):
        # Para o listener atual se existir
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

        # Cria um novo listener
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=None,
            suppress=False
        )
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            try:
                self.listener.stop()
                self.listener = None
            except:
                pass

    def on_press(self, key):
        try:
            # Verifica se estamos no menu principal
            if self.current_frame == "main":
                if key == keyboard.Key.down:
                    self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                    self.highlight_menu_option()
                    self.announce_current_option()
                elif key == keyboard.Key.up:
                    self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                    self.highlight_menu_option()
                    self.announce_current_option()
                elif key == keyboard.Key.enter or key == keyboard.Key.space:
                    if self.current_selection == 0:
                        self.show_level_selection()
                    else:
                        self.start_free_mode()

            # Verifica se estamos na seleção de nível
            elif self.current_frame == "level":
                if key == keyboard.Key.down:
                    self.level_selection = (self.level_selection + 1) % len(self.level_options)
                    self.highlight_level_option()
                    self.announce_current_level_option()
                elif key == keyboard.Key.up:
                    self.level_selection = (self.level_selection - 1) % len(self.level_options)
                    self.highlight_level_option()
                    self.announce_current_level_option()
                elif key == keyboard.Key.enter or key == keyboard.Key.space:
                    if self.level_selection == 0:
                        self.start_game_with_level("Fácil")
                    elif self.level_selection == 1:
                        self.start_game_with_level("Médio")
                    elif self.level_selection == 2:
                        self.start_game_with_level("Difícil")
                    elif self.level_selection == 3:
                        self.show_main_menu()
                elif key == keyboard.Key.esc:
                    self.show_main_menu()

        except Exception as e:
            print(f"Erro no listener: {e}")

    def announce_menu_options(self):
        """Anuncia as opções do menu principal usando TTS"""
        announcement = (
            "Bem-vindo ao KeyEarn. Use as setas para cima e para baixo para navegar. "
            "Pressione Enter ou Espaço para selecionar. "
            f"Opção atual: {self.menu_options[self.current_selection]}"
        )
        threading.Thread(
            target=lambda: play_audio(text_to_speech(announcement)),
            daemon=True
        ).start()

    def announce_current_option(self):
        """Anuncia a opção atual selecionada"""
        threading.Thread(
            target=lambda: play_audio(text_to_speech(self.menu_options[self.current_selection])),
            daemon=True
        ).start()

    def announce_level_options(self):
        """Anuncia as opções de nível disponíveis"""
        announcement = (
            "Selecione o nível de dificuldade. Use as setas para cima e para baixo para navegar. "
            "Pressione Enter ou Espaço para selecionar. Pressione ESC para voltar. "
            f"Opção atual: {self.level_options[self.level_selection]}"
        )
        threading.Thread(
            target=lambda: play_audio(text_to_speech(announcement)),
            daemon=True
        ).start()

    def announce_current_level_option(self):
        """Anuncia a opção de nível atual selecionada"""
        threading.Thread(
            target=lambda: play_audio(text_to_speech(self.level_options[self.level_selection])),
            daemon=True
        ).start()

    def show_main_menu(self):
        # Destrói o conteúdo atual, se houver
        if self.current_game_instance:
            try:
                self.current_game_instance.main_frame.destroy()
            except:
                pass
            self.current_game_instance = None

        # Destrói o frame de nível, se houver
        if hasattr(self, 'level_frame') and self.level_frame:
            try:
                self.level_frame.destroy()
            except:
                pass

        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.current_frame = "main"
        title_label = ttk.Label(
            self.main_frame,
            text="KeyEarn\nTreino de Digitação",  # \n para quebra de linha
            font=("Helvetica", 36, "bold"),
            foreground="white",
            background=BACKGROUND_COLOR,
            justify='center'  # Centraliza o texto
        )
        title_label.pack(pady=40)

        # Armazena os botões para poder destacá-los
        self.menu_buttons = []

        standard_game_btn = ttk.Button(
            self.main_frame,
            text="Modo Jogo Padrão",
            command=self.show_level_selection,
            style="TButton"
        )
        standard_game_btn.pack(pady=15)
        self.menu_buttons.append(standard_game_btn)

        free_play_btn = ttk.Button(
            self.main_frame,
            text="Modo Jogo Livre",
            command=self.start_free_mode,
            style="TButton"
        )
        free_play_btn.pack(pady=15)
        self.menu_buttons.append(free_play_btn)

        # Destacar a opção atual
        self.highlight_menu_option()

        # Configurar o listener de teclado novamente
        self.setup_keyboard_listener()

    def highlight_menu_option(self):
        """Destaca visualmente a opção atual do menu"""
        for i, button in enumerate(self.menu_buttons):
            if i == self.current_selection:
                button.configure(style="Selected.TButton")
            else:
                button.configure(style="TButton")

    def show_level_selection(self):
        try:
            self.main_frame.destroy()
        except:
            pass

        self.level_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.level_frame.pack(expand=True, fill=tk.BOTH)
        self.current_frame = "level"

        title_label = ttk.Label(
            self.level_frame,
            text="Selecione o Nível de Dificuldade",
            font=("Helvetica", 24, "bold"),
            foreground="white",
            background=BACKGROUND_COLOR
        )
        title_label.pack(pady=30)

        # Anuncia as opções de nível
        self.announce_level_options()

        # Armazena os botões de nível para destacá-los
        self.level_buttons = []

        # Botões para cada nível
        easy_btn = ttk.Button(
            self.level_frame,
            text="Fácil",
            command=lambda: self.start_game_with_level("Fácil"),
            style="TButton"
        )
        easy_btn.pack(pady=10)
        self.level_buttons.append(easy_btn)

        medium_btn = ttk.Button(
            self.level_frame,
            text="Médio",
            command=lambda: self.start_game_with_level("Médio"),
            style="TButton"
        )
        medium_btn.pack(pady=10)
        self.level_buttons.append(medium_btn)

        hard_btn = ttk.Button(
            self.level_frame,
            text="Difícil",
            command=lambda: self.start_game_with_level("Difícil"),
            style="TButton"
        )
        hard_btn.pack(pady=10)
        self.level_buttons.append(hard_btn)

        # Adiciona o botão "Voltar"
        back_btn = ttk.Button(
            self.level_frame,
            text="← Voltar",
            command=self.show_main_menu,
            style="TButton"
        )
        back_btn.pack(pady=20)
        self.level_buttons.append(back_btn)

        # Reinicia a seleção para a primeira opção
        self.level_selection = 0
        self.highlight_level_option()

        # Configura o listener de teclado novamente
        self.setup_keyboard_listener()

    def highlight_level_option(self):
        """Destaca visualmente a opção de nível atual"""
        for i, button in enumerate(self.level_buttons):
            if i == self.level_selection:
                button.configure(style="Selected.TButton")
                # Adiciona um indicador visual adicional
                button.configure(text=f"➤ {self.level_options[i]}")
            else:
                button.configure(style="TButton")
                button.configure(text=self.level_options[i])

    def start_game_with_level(self, level):
        level_map = {
            "Fácil": 1,
            "Médio": 2,
            "Difícil": 3
        }

        # Anuncia a seleção do nível
        announcement = f"Iniciando modo {level}. Preparando o jogo..."
        threading.Thread(
            target=lambda: play_audio(text_to_speech(announcement)),
            daemon=True
        ).start()

        try:
            self.level_frame.destroy()
        except:
            pass

        self.current_frame = "game"
        self.current_game_instance = TypingGame(self.root, self.show_main_menu, level_map[level])

    def start_free_mode(self):
        # Anuncia a seleção do modo livre
        announcement = "Iniciando modo livre. Preparando o jogo..."
        threading.Thread(
            target=lambda: play_audio(text_to_speech(announcement)),
            daemon=True
        ).start()

        try:
            self.main_frame.destroy()
        except:
            pass

        self.current_frame = "game"
        self.current_game_instance = FreeModeGame(self.root, self.show_main_menu)


def main():
    root = tk.Tk()

    # Configurar estilo para botão selecionado
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    style.configure("Selected.TButton",
                    font=("Helvetica", 14, "bold"),
                    padding=12,
                    background="#3498db",
                    foreground="black",
                    borderwidth=2,
                    relief="solid")

    app = MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()