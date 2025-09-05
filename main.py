# main.py

import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from datetime import datetime
import sys
import os

# Importa as classes de jogo
from typing_game import TypingGame
from free_mode import FreeModeGame 

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
        
        # Destrói o frame de nível, se houver
        if hasattr(self, 'level_frame') and self.level_frame:
            self.level_frame.destroy()

        # Cria e exibe o menu principal
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
            command=self.show_level_selection,
            style="TButton"
        )
        standard_game_btn.pack(pady=15)

        free_play_btn = ttk.Button(
            self.main_frame,
            text="Modo Jogo Livre",
            command=self.start_free_mode,
            style="TButton"
        )
        free_play_btn.pack(pady=15)

    def show_level_selection(self):
        self.main_frame.destroy()
        
        self.level_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.level_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(
            self.level_frame,
            text="Selecione o Nível de Dificuldade",
            font=("Helvetica", 24, "bold"),
            foreground="white",
            background=BACKGROUND_COLOR
        )
        title_label.pack(pady=30)
        
        # Botões para cada nível
        easy_btn = ttk.Button(
            self.level_frame,
            text="Fácil",
            command=lambda: self.start_game_with_level("Fácil"),
            style="TButton"
        )
        easy_btn.pack(pady=10)

        medium_btn = ttk.Button(
            self.level_frame,
            text="Médio",
            command=lambda: self.start_game_with_level("Médio"),
            style="TButton"
        )
        medium_btn.pack(pady=10)

        hard_btn = ttk.Button(
            self.level_frame,
            text="Difícil",
            command=lambda: self.start_game_with_level("Difícil"),
            style="TButton"
        )
        hard_btn.pack(pady=10)

        # Adiciona o botão "Voltar"
        back_btn = ttk.Button(
            self.level_frame,
            text="← Voltar",
            command=self.show_main_menu,
            style="TButton"
        )
        back_btn.pack(pady=20)


    def start_game_with_level(self, level):
        # Destrói o frame de seleção de nível e inicia o jogo padrão
        self.level_frame.destroy()
        # Passa o nível de dificuldade para a classe TypingGame
        self.current_game_instance = TypingGame(self.root, self.show_main_menu, level)

    def start_free_mode(self):
        self.main_frame.destroy()
        self.current_game_instance = FreeModeGame(self.root, self.show_main_menu)

def main():
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()