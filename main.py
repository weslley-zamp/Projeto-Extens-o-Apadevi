# main.py

import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
import threading

from typing_game import TypingGame
from free_mode import FreeModeGame
from ranking_screen import RankingScreen  # 👈 Import da tela de ranking

from config import (
    load_config,
    save_config,
    DEFAULT_CONFIG,
    COLOR_MAP,
    parse_color_name,
    get_color_name_from_hex,
)
from services.tts_service import text_to_speech
from utils.audio_player import play_audio


class MainMenu:
    def __init__(self, root):
        self.root = root
        self.current_game_instance = None
        self.listener = None
        self.current_selection = 0
        self.level_selection = 0
        self.menu_options = ["Modo Jogo Padrão", "Modo Jogo Livre", "Ranking", "Configurações"]  # 👈 Adicionado Ranking
        self.level_options = ["Fácil", "Médio", "Difícil", "Voltar"]
        self.current_frame = None

        # Carrega a config
        raw_config = load_config() or {}
        self.config = {}
        for k, default_val in DEFAULT_CONFIG.items():
            v = raw_config.get(k, default_val)
            if "COLOR" in k:
                self.config[k] = parse_color_name(v, DEFAULT_CONFIG[k])
            elif k in ["FONT_SIZE"]:
                try:
                    self.config[k] = int(v)
                except:
                    self.config[k] = DEFAULT_CONFIG[k]
            else:
                self.config[k] = v

        self.setup_window()
        self.setup_keyboard_listener()
        self.show_main_menu()
        self.announce_menu_options()

    # =================== CONFIGURAÇÕES DA JANELA ===================
    def setup_window(self):
        bg = self.config.get(
            "BACKGROUND_COLOR",
            parse_color_name(DEFAULT_CONFIG["BACKGROUND_COLOR"], DEFAULT_CONFIG["BACKGROUND_COLOR"]),
        )
        self.root.title("KeyEarn")
        self.root.configure(bg=bg)
        self.root.geometry("1080x720")
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    # =================== CONTROLE DE TECLADO ===================
    def setup_keyboard_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        self.listener = keyboard.Listener(on_press=self.on_press)
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
            if self.current_frame == "main":
                if key == keyboard.Key.down:
                    self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                    self.highlight_menu_option()
                    self.announce_current_option()
                elif key == keyboard.Key.up:
                    self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                    self.highlight_menu_option()
                    self.announce_current_option()
                elif key in [keyboard.Key.enter, keyboard.Key.space]:
                    if self.current_selection == 0:
                        self.show_level_selection()
                    elif self.current_selection == 1:
                        self.start_free_mode()
                    elif self.current_selection == 2:
                        self.show_ranking()  # 👈 Ação para abrir o ranking
                    else:
                        self.open_settings()

            elif self.current_frame == "level":
                if key == keyboard.Key.down:
                    self.level_selection = (self.level_selection + 1) % len(self.level_options)
                    self.highlight_level_option()
                    self.announce_current_level_option()
                elif key == keyboard.Key.up:
                    self.level_selection = (self.level_selection - 1) % len(self.level_options)
                    self.highlight_level_option()
                    self.announce_current_level_option()
                elif key in [keyboard.Key.enter, keyboard.Key.space]:
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

    # =================== ANÚNCIOS POR VOZ ===================
    def announce_menu_options(self):
        announcement = (
            "Bem-vindo ao KeyEarn. Use as setas para navegar. "
            f"Opção atual: {self.menu_options[self.current_selection]}"
        )
        threading.Thread(target=lambda: play_audio(text_to_speech(announcement)), daemon=True).start()

    def announce_current_option(self):
        threading.Thread(
            target=lambda: play_audio(text_to_speech(self.menu_options[self.current_selection])),
            daemon=True,
        ).start()

    def announce_level_options(self):
        announcement = (
            "Selecione o nível de dificuldade. "
            f"Opção atual: {self.level_options[self.level_selection]}"
        )
        threading.Thread(target=lambda: play_audio(text_to_speech(announcement)), daemon=True).start()

    def announce_current_level_option(self):
        threading.Thread(
            target=lambda: play_audio(text_to_speech(self.level_options[self.level_selection])),
            daemon=True,
        ).start()

    # =================== TELAS PRINCIPAIS ===================
    def show_main_menu(self):
        if self.current_game_instance:
            try:
                self.current_game_instance.main_frame.destroy()
            except:
                pass
            self.current_game_instance = None

        for frame in ["level_frame", "settings_frame"]:
            if hasattr(self, frame) and getattr(self, frame):
                try:
                    getattr(self, frame).destroy()
                except:
                    pass

        bg_hex = self.config.get(
            "BACKGROUND_COLOR",
            parse_color_name(DEFAULT_CONFIG["BACKGROUND_COLOR"], DEFAULT_CONFIG["BACKGROUND_COLOR"]),
        )

        self.main_frame = tk.Frame(
            self.root, bg=bg_hex, padx=20, pady=20
        )
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.current_frame = "main"

        title_label = tk.Label(
            self.main_frame,
            text="KeyEarn\nTreino de Digitação",
            font=("Helvetica", self.config["FONT_SIZE"] + 20, "bold"),
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            bg=bg_hex,
            justify="center",
        )
        title_label.pack(pady=40)

        self.menu_buttons = []
        for option in self.menu_options:
            btn = ttk.Button(
                self.main_frame,
                text=option,
                command=lambda opt=option: self.menu_action(opt),
                style="TButton",
            )
            btn.pack(pady=15)
            self.menu_buttons.append(btn)

        self.highlight_menu_option()
        self.setup_keyboard_listener()

    def menu_action(self, option):
        if option == "Modo Jogo Padrão":
            self.show_level_selection()
        elif option == "Modo Jogo Livre":
            self.start_free_mode()
        elif option == "Ranking":
            self.show_ranking()  # 👈 Abre a tela de ranking
        elif option == "Configurações":
            self.open_settings()

    def highlight_menu_option(self):
        for i, button in enumerate(self.menu_buttons):
            if i == self.current_selection:
                button.configure(style="Selected.TButton")
            else:
                button.configure(style="TButton")

    def show_ranking(self):
        self.main_frame.destroy()
        self.current_frame = "ranking"
        RankingScreen(self.root, self.show_main_menu)  # 👈 Cria a tela de ranking

    def show_level_selection(self):
        self.main_frame.destroy()

        bg_hex = self.config.get(
            "BACKGROUND_COLOR",
            parse_color_name(DEFAULT_CONFIG["BACKGROUND_COLOR"], DEFAULT_CONFIG["BACKGROUND_COLOR"]),
        )

        self.level_frame = tk.Frame(
            self.root,
            bg=bg_hex,
            padx=20,
            pady=20,
        )
        self.level_frame.pack(expand=True, fill=tk.BOTH)
        self.current_frame = "level"

        title_label = tk.Label(
            self.level_frame,
            text="Selecione o Nível de Dificuldade",
            font=("Helvetica", self.config["FONT_SIZE"], "bold"),
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            bg=bg_hex,
        )
        title_label.pack(pady=30)

        self.announce_level_options()
        self.level_buttons = []

        for level in self.level_options:
            btn = ttk.Button(
                self.level_frame,
                text=level,
                command=lambda lvl=level: self.start_game_with_level(lvl) if lvl != "Voltar" else self.show_main_menu(),
                style="TButton",
            )
            btn.pack(pady=10)
            self.level_buttons.append(btn)

        self.level_selection = 0
        self.highlight_level_option()
        self.setup_keyboard_listener()

    def highlight_level_option(self):
        for i, button in enumerate(self.level_buttons):
            if i == self.level_selection:
                button.configure(style="Selected.TButton", text=f"➤ {self.level_options[i]}")
            else:
                button.configure(style="TButton", text=self.level_options[i])

    def start_game_with_level(self, level):
        level_map = {"Fácil": 1, "Médio": 2, "Difícil": 3}
        announcement = f"Iniciando modo {level}."
        threading.Thread(target=lambda: play_audio(text_to_speech(announcement)), daemon=True).start()

        self.level_frame.destroy()
        self.current_frame = "game"
        self.current_game_instance = TypingGame(self.root, self.show_main_menu, level_map[level])

    def start_free_mode(self):
        threading.Thread(
            target=lambda: play_audio(text_to_speech("Iniciando modo livre.")),
            daemon=True,
        ).start()

        self.main_frame.destroy()
        self.current_frame = "game"
        self.current_game_instance = FreeModeGame(self.root, self.show_main_menu)

    # =================== CONFIGURAÇÕES ===================
    def open_settings(self):
        self.main_frame.destroy()

        bg_hex = self.config.get(
            "BACKGROUND_COLOR",
            parse_color_name(DEFAULT_CONFIG["BACKGROUND_COLOR"], DEFAULT_CONFIG["BACKGROUND_COLOR"]),
        )

        self.settings_frame = tk.Frame(
            self.root,
            bg=bg_hex,
            padx=20,
            pady=20,
        )
        self.settings_frame.pack(expand=True, fill=tk.BOTH)
        self.current_frame = "settings"

        title = tk.Label(
            self.settings_frame,
            text="Configurações",
            font=("Helvetica", self.config["FONT_SIZE"], "bold"),
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            bg=bg_hex,
        )
        title.pack(pady=20)

        self.entries = {}

        # ========== CAMPOS ==========
        tk.Label(
            self.settings_frame,
            text="Cor de fundo:",
            bg=bg_hex,
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            anchor="w",
        ).pack(fill="x")
        bg_combo = ttk.Combobox(self.settings_frame, values=list(COLOR_MAP.keys()), state="readonly")
        bg_combo.set(get_color_name_from_hex(self.config["BACKGROUND_COLOR"]))
        bg_combo.pack(fill="x", pady=5)
        self.entries["BACKGROUND_COLOR"] = bg_combo

        tk.Label(
            self.settings_frame,
            text="Cor da letra:",
            bg=bg_hex,
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            anchor="w",
        ).pack(fill="x")
        fg_combo = ttk.Combobox(self.settings_frame, values=list(COLOR_MAP.keys()), state="readonly")
        fg_combo.set(get_color_name_from_hex(self.config["FOREGROUND_COLOR"]))
        fg_combo.pack(fill="x", pady=5)
        self.entries["FOREGROUND_COLOR"] = fg_combo

        tk.Label(
            self.settings_frame,
            text="Tamanho da fonte:",
            bg=bg_hex,
            fg=self.config.get("FOREGROUND_COLOR", "white"),
            anchor="w",
        ).pack(fill="x")
        size_combo = ttk.Combobox(self.settings_frame, values=[16, 20, 24, 28, 32, 36, 40, 56, 70, 80], state="readonly")
        size_combo.set(self.config["FONT_SIZE"])
        size_combo.pack(fill="x", pady=5)
        self.entries["FONT_SIZE"] = size_combo

        buttons_frame = tk.Frame(self.settings_frame, bg=bg_hex)
        buttons_frame.pack(pady=15)

        save_btn = tk.Button(buttons_frame, text="Salvar", command=self.save_settings)
        save_btn.pack(side="left", padx=5)
        back_btn = tk.Button(buttons_frame, text="Voltar", command=self.show_main_menu)
        back_btn.pack(side="left", padx=5)

    def save_settings(self):
        save_dict = {}
        for key, widget in self.entries.items():
            value = widget.get()
            if "COLOR" in key:
                hex_val = parse_color_name(value, DEFAULT_CONFIG[key])
                self.config[key] = hex_val
                save_dict[key] = value
            elif key == "FONT_SIZE":
                try:
                    ival = int(value)
                    self.config[key] = ival
                    save_dict[key] = ival
                except:
                    self.config[key] = DEFAULT_CONFIG[key]
                    save_dict[key] = DEFAULT_CONFIG[key]
            else:
                self.config[key] = value
                save_dict[key] = value

        try:
            save_config(save_dict)
            threading.Thread(target=lambda: play_audio(text_to_speech("Configurações salvas.")), daemon=True).start()
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

        try:
            self.root.configure(bg=self.config["BACKGROUND_COLOR"])
        except:
            pass
        self.show_main_menu()


def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)
    style.configure(
        "Selected.TButton",
        font=("Helvetica", 14, "bold"),
        padding=12,
        background="#3498db",
        foreground="black",
        borderwidth=2,
        relief="solid",
    )

    app = MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
