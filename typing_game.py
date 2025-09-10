import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
# <--- ALTERAÇÃO 1: Importar a nova função 'start_new_game_words' ---
from services.word_generator import get_word_by_level, start_new_game_words
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words
import winsound
import threading
from datetime import datetime
import sys
import os
import unicodedata

# Agora importamos o CONFIG (dicionário) e o SoundPlayer do config.py
from config import SoundPlayer, CONFIG


class TypingGame:
    def __init__(self, root, switch_to_main_menu, level):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.current_level = level
        self.cfg = CONFIG  # copia das configurações atuais
        self.sound_enabled = self.check_sound_support()
        self.listener = None
        self.last_key_time = 0
        self.game_in_progress = False
        self.accent_buffer = None

        self.setup_ui()
        self.start_new_game()

    def setup_window(self):
        pass

    def check_sound_support(self):
        try:
            winsound.Beep(1000, 10)
            return True
        except:
            return False

    def setup_ui(self):
        # Sempre recarrega config atualizada
        self.cfg = CONFIG  

        # Lê valores do config com defaults
        bg = self.cfg.get("BACKGROUND_COLOR", "#2c3e50")
        font_size = self.cfg.get("FONT_SIZE", 28)
        padding = self.cfg.get("PADDING", 30)
        typing_color = self.cfg.get("TYPING_COLOR", "#3498db")
        fg_color = self.cfg.get("FOREGROUND_COLOR", "white")  # opcional

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", font_size), background=bg)
        style.configure("Stats.TLabel", font=("Helvetica", 14), background=bg)

        # Janela principal do jogo
        self.main_frame = tk.Frame(self.root, bg=bg, padx=padding, pady=padding)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.game_frame = tk.Frame(self.main_frame, bg=bg)
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        self.stats_frame = tk.Frame(self.main_frame, bg=bg)

        # Rótulos principais
        self.word_label = ttk.Label(
            self.game_frame,
            text="",
            font=("Helvetica", font_size),
            foreground=fg_color,
            background=bg
        )
        self.word_label.pack(pady=20)

        self.feedback_label = ttk.Label(
            self.game_frame,
            text="",
            font=("Helvetica", font_size),
            foreground=typing_color,
            background=bg
        )
        self.feedback_label.pack(pady=20)

        self.progress_label = ttk.Label(
            self.game_frame,
            text="Palavra 1/30",
            font=("Helvetica", 14),
            foreground=self.cfg.get("PROGRESS_COLOR", "#bdc3c7"),
            background=bg
        )
        self.progress_label.pack()

        self.back_btn = ttk.Button(
            self.game_frame,
            text="← Voltar ao Menu",
            command=self.end_game,
            style="TButton"
        )
        self.back_btn.pack(pady=20)

    def start_new_game(self):
        # Recarrega configuração no início da partida (caso tenha mudado)
        self.cfg = CONFIG  
        WORDS_PER_GAME = self.cfg.get("WORDS_PER_GAME", 30)

        # <--- ALTERAÇÃO 2: Chamar a função para resetar a lista de palavras ---
        start_new_game_words()

        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

        self.stats_frame.pack_forget()
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        self.game_stats = {
            'total_words': WORDS_PER_GAME,
            'correct_words': 0,
            'incorrect_words': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'current_word_index': 0,
            'words': [get_word_by_level(self.current_level) for _ in range(WORDS_PER_GAME)],
            'level': self.current_level,
            'total_chars': 0,
            'correct_chars': 0,
            'word_completed': False,
            'total_words_typed': 0
        }

        self.typed_word = ""
        self.current_index = 0
        self.last_key_time = 0
        self.accent_buffer = None
        self.game_in_progress = True
        self.show_current_word()
        self.setup_keyboard_listener()

    def show_current_word(self):
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            self.word_label.config(text=current_word)

            # atualiza preview do feedback usando _ por cada letra
            self.feedback_label.config(text=" ".join("_" * len(current_word)))

            self.progress_label.config(
                text=f"Palavra {self.game_stats['current_word_index'] + 1}/{self.game_stats['total_words']}"
            )

            # TTS da palavra
            threading.Thread(
                target=lambda: play_audio(text_to_speech(f"A palavra é: {current_word}")),
                daemon=True
            ).start()
        except Exception as e:
            print(f"Erro ao mostrar palavra atual: {e}")

    def setup_keyboard_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

        self.listener = None
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
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

    def combine_accent(self, accent, vowel):
        accent_map = {
            '´': {
                'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'
            },
            '`': {
                'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'
            },
            '^': {
                'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'
            },
            '~': {
                'a': 'ã', 'o': 'õ', 'n': 'ñ',
                'A': 'Ã', 'O': 'Õ', 'N': 'Ñ'
            },
            '"': {
                'u': 'ü', 'U': 'Ü'
            }
        }

        if accent in accent_map and vowel in accent_map[accent]:
            return accent_map[accent][vowel]
        return vowel

    def on_press(self, key):
        if not self.game_in_progress:
            if key == keyboard.Key.esc:
                self.stop_listener()
                self.switch_to_main_menu()
                return
            elif key == keyboard.Key.space:
                self.stop_listener()
                self.start_new_game()
                return
            return

        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]

            if key == keyboard.Key.backspace:
                if len(self.typed_word) > 0:
                    self.typed_word = self.typed_word[:-1]
                    self.current_index = len(self.typed_word) - 1
                    if self.sound_enabled:
                        threading.Thread(target=SoundPlayer.play_backspace, daemon=True).start()
                    self.update_ui()
                self.accent_buffer = None
                return

            if key == keyboard.Key.esc:
                self.end_game()
                return

            # ✅ Agora só valida quando o usuário pressiona ENTER
            if key == keyboard.Key.enter:
                if not self.game_stats['word_completed']:
                    result = compare_words(current_word, self.typed_word)
                    if result is None:
                        self.handle_success()
                    else:
                        self.handle_error()
                return

            try:
                char = key.char
            except AttributeError:
                return  # ignora outras teclas

            # Tratamento de acentos
            accents = ['´', '`', '^', '~', '"']
            if char in accents:
                self.accent_buffer = char
                return

            if len(self.typed_word) >= len(current_word):
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
                return

            if self.accent_buffer and char in 'aeiouAEIOUunUN':
                combined_char = self.combine_accent(self.accent_buffer, char)
                self.typed_word += combined_char
                self.accent_buffer = None
            else:
                if self.accent_buffer:
                    self.typed_word += self.accent_buffer
                    self.accent_buffer = None
                self.typed_word += char

            self.current_index = len(self.typed_word) - 1

            self.game_stats['total_chars'] += 1
            # pega cores atuais do config
            correct_color = CONFIG.get("CORRECT_COLOR", "#27ae60")
            error_color = CONFIG.get("ERROR_COLOR", "#e74c3c")

            if self.current_index < len(current_word) and self.typed_word[-1] == current_word[self.current_index]:
                self.game_stats['correct_chars'] += 1
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_letter_correct, daemon=True).start()
            else:
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_error, daemon=True).start()

            self.update_ui()

        except Exception as e:
            print(f"Erro ao processar tecla: {e}")

    def on_release(self, key):
        pass

    def handle_error(self):
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_error, daemon=True).start()

            self.game_stats['incorrect_words'] += 1
            self.game_stats['total_words_typed'] += 1
            self.game_stats['word_completed'] = True
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com erro: {e}")

    def handle_success(self):
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_word_correct, daemon=True).start()

            self.game_stats['correct_words'] += 1
            self.game_stats['total_words_typed'] += 1
            self.game_stats['word_completed'] = True
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com sucesso: {e}")

    def next_word(self):
        try:
            self.game_stats['current_word_index'] += 1
            self.typed_word = ""
            self.current_index = 0
            self.accent_buffer = None
            self.game_stats['word_completed'] = False

            if self.game_stats['current_word_index'] < self.game_stats['total_words']:
                self.show_current_word()
            else:
                self.end_game()
        except Exception as e:
            print(f"Erro ao avançar para próxima palavra: {e}")

    def end_game(self):
        try:
            self.game_stats['end_time'] = datetime.now()
            self.game_in_progress = False
            self.show_game_stats()
            self.stop_listener()

            threading.Thread(
                target=self.announce_stats,
                daemon=True
            ).start()
            self.setup_keyboard_listener()

        except Exception as e:
            print(f"Erro ao finalizar jogo: {e}")

    def announce_stats(self):
        total_time = (self.game_stats['end_time'] - self.game_stats['start_time']).total_seconds()
        minutes = total_time / 60
        wpm = self.game_stats['total_words_typed'] / minutes if minutes > 0 else 0
        levels = {1: "Fácil", 2: "Médio", 3: "Difícil"}
        level_name = levels.get(self.game_stats.get('level', 1), "Fácil")
        accuracy = (self.game_stats['correct_chars'] / self.game_stats['total_chars'] * 100) if self.game_stats['total_chars'] > 0 else 0

        stats_text = (
            f"Partida concluída! "
            f"Nível: {level_name}. "
            f"Palavras corretas: {self.game_stats['correct_words']} de {self.game_stats['total_words']}. "
            f"Palavras incorretas: {self.game_stats['incorrect_words']}. "
            f"Tempo total: {int(total_time)} segundos. "
            f"Velocidade: {int(wpm)} palavras por minuto. "
            f"Precisão: {int(accuracy)} por cento. "
            f"Pressione a barra de espaço para uma nova partida ou Esc para voltar ao menu principal."
        )
        play_audio(text_to_speech(stats_text))

    def show_game_stats(self):
        try:
            self.cfg = CONFIG  
            total_time = (self.game_stats['end_time'] - self.game_stats['start_time']).total_seconds()
            minutes = total_time / 60
            wpm = self.game_stats['total_words_typed'] / minutes if minutes > 0 else 0
            accuracy = (self.game_stats['correct_chars'] / self.game_stats['total_chars'] * 100) if self.game_stats['total_chars'] > 0 else 0
            levels = {1: "Fácil", 2: "Médio", 3: "Difícil"}
            level_name = levels.get(self.game_stats.get('level', 1), "Fácil")
            self.game_frame.pack_forget()
            self.stats_frame.pack(expand=True, fill=tk.BOTH)
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
                
            ttk.Label(
                self.stats_frame,
                text="Partida Concluída!",
                font=("Helvetica", 24),
                foreground=self.cfg.get("FOREGROUND_COLOR", "white"),
                background=self.cfg.get("BACKGROUND_COLOR", "#2c3e50")
            ).pack(pady=20)

            stats_text = (
                f"Nível: {level_name}\n"
                f"Palavras corretas: {self.game_stats['correct_words']}/{self.game_stats['total_words']}\n"
                f"Palavras incorretas: {self.game_stats['incorrect_words']}\n"
                f"Total de palavras digitadas: {self.game_stats['total_words_typed']}\n"
                f"Tempo total: {total_time:.1f} segundos\n"
                f"Velocidade: {wpm:.1f} palavras por minuto\n"
                f"Precisão: {accuracy:.1f}%\n"
                f"Caracteres: {self.game_stats['correct_chars']}/{self.game_stats['total_chars']}\n\n"
                f"Pressione a barra de espaço para uma nova partida\n"
                f"Pressione Esc para voltar ao menu"
            )

            ttk.Label(
                self.stats_frame,
                text=stats_text,
                style="Stats.TLabel",
                justify=tk.LEFT
            ).pack(pady=20)

            back_btn = ttk.Button(
                self.stats_frame,
                text="← Voltar ao Menu",
                command=self.end_game_by_button,
                style="TButton"
            )
            back_btn.pack(pady=20)
        except Exception as e:
            print(f"Erro ao mostrar estatísticas: {e}")

    def end_game_by_button(self):
        self.stop_listener()
        self.switch_to_main_menu()

    def update_ui(self):
        try:
            self.cfg = CONFIG  
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            feedback_chars = []
            correct_color = self.cfg.get("CORRECT_COLOR", "#27ae60")
            error_color = self.cfg.get("ERROR_COLOR", "#e74c3c")
            typing_color = self.cfg.get("TYPING_COLOR", "#3498db")
            for i in range(len(current_word)):
                if i < len(self.typed_word):
                    color = correct_color if self.typed_word[i] == current_word[i] else error_color
                    feedback_chars.append((self.typed_word[i], color))
                else:
                    feedback_chars.append(("_", typing_color))
            self.feedback_label.config(text=" ".join([char for char, _ in feedback_chars]))

            if self.current_index < len(feedback_chars):
                self.feedback_label.config(foreground=feedback_chars[self.current_index][1])
            else:
                self.feedback_label.config(foreground=typing_color)
        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")
