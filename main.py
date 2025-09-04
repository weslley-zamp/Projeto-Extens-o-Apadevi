# main.py

import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from datetime import datetime
import sys
import os

# Importa as classes de jogo
from typing_game import TypingGame
from free_play_game import FreePlayGame

# Importa as configurações do novo arquivo
from config import (
    BACKGROUND_COLOR,
    FONT_SIZE,
    PADDING
)

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.current_game_instance = None
        self.setup_window()
        self.show_main_menu()

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

    def show_main_menu(self):
        # Destrói o conteúdo atual, se houver
        if self.current_game_instance:
            self.current_game_instance.main_frame.destroy()
            self.current_game_instance = None
        
        # Cria e exibe o menu
        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(
            self.main_frame,
            text="KeyEarn - Treino de Digitação",
            font=("Helvetica", 36, "bold"),
            foreground="white",
            background=BACKGROUND_COLOR
        )
        title_label.pack(pady=40)

        standard_game_btn = ttk.Button(
            self.main_frame,
            text="Modo Jogo Padrão",
            command=self.start_standard_game,
            style="TButton"
        )
        standard_game_btn.pack(pady=15)

        free_play_btn = ttk.Button(
            self.main_frame,
            text="Modo Jogo Livre",
            command=self.start_free_play_game,
            style="TButton"
        )
        free_play_btn.pack(pady=15)

    def start_standard_game(self):
        # Destrói o menu e inicia o jogo padrão
        self.main_frame.destroy()
        self.current_game_instance = TypingGame(self.root, self.show_main_menu)

    def start_free_play_game(self):
        # Destrói o menu e inicia o jogo livre
        self.main_frame.destroy()
        self.current_game_instance = FreePlayGame(self.root, self.show_main_menu)

def main():
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()