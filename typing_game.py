# typing_game.py
import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from services.word_generator import get_word_by_level
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words
import winsound
import threading
from datetime import datetime
import sys
import os

# Importa as configurações do novo arquivo config.py
from config import (
    SoundPlayer,
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    ERROR_COLOR,
    FONT_SIZE,
    TYPING_COLOR,
    PADDING,
    WORDS_PER_GAME
)

class TypingGame:
    def __init__(self, root, switch_to_main_menu, level):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.current_level = level
        self.sound_enabled = self.check_sound_support()
        self.listener = None
        self.last_key_time = 0
        self.game_in_progress = False # Novo atributo para controlar o estado do jogo
        
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
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.configure("TLabel", font=("Helvetica", FONT_SIZE), background=BACKGROUND_COLOR)
        style.configure("Stats.TLabel", font=("Helvetica", 14), background=BACKGROUND_COLOR)

        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.game_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        self.stats_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        
        self.word_label = ttk.Label(
            self.game_frame,
            text="",
            font=("Helvetica", FONT_SIZE),
            foreground="white"
        )
        self.word_label.pack(pady=20)

        self.feedback_label = ttk.Label(
            self.game_frame,
            text="",
            font=("Helvetica", FONT_SIZE),
            foreground=TYPING_COLOR
        )
        self.feedback_label.pack(pady=20)

        self.progress_label = ttk.Label(
            self.game_frame,
            text="Palavra 1/30",
            font=("Helvetica", 14),
            foreground="#bdc3c7"
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
            'level': self.current_level
        }
        
        self.typed_word = ""
        self.current_index = 0
        self.last_key_time = 0
        self.game_in_progress = True # O jogo está em progresso
        self.show_current_word()
        self.setup_keyboard_listener()

    def show_current_word(self):
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            self.word_label.config(text=current_word)
            self.feedback_label.config(text=" ".join("_" * len(current_word)))
            self.progress_label.config(
                text=f"Palavra {self.game_stats['current_word_index'] + 1}/{self.game_stats['total_words']}"
            )
            
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

    def on_press(self, key):
        # Lógica para o final do jogo
        if not self.game_in_progress:
            if key == keyboard.Key.esc:
                self.stop_listener()
                self.switch_to_main_menu()
                return
            elif key == keyboard.Key.space:
                self.stop_listener()
                self.start_new_game()
                return
            return # Sai da função se o jogo não estiver em progresso

        # Lógica normal de digitação
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]

            if key == keyboard.Key.backspace:
                if len(self.typed_word) > 0:
                    self.typed_word = self.typed_word[:-1]
                    self.current_index = len(self.typed_word) - 1
                    if self.sound_enabled:
                        threading.Thread(target=SoundPlayer.play_backspace, daemon=True).start()
                    self.update_ui()
                return

            if key == keyboard.Key.esc:
                self.end_game()
                return

            try:
                char = key.char
            except AttributeError:
                if key == keyboard.Key.space:
                    if len(self.typed_word) == len(current_word) and compare_words(current_word, self.typed_word) is None:
                        self.handle_success()
                    else:
                        self.handle_error()
                return

            if len(self.typed_word) >= len(current_word):
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
                return
                
            self.typed_word += char
            self.current_index = len(self.typed_word) - 1
            
            if self.current_index < len(current_word) and char == current_word[self.current_index]:
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_letter_correct, daemon=True).start()
            else:
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            
            self.update_ui()
            
            if len(self.typed_word) == len(current_word):
                if compare_words(current_word, self.typed_word) is None:
                    self.handle_success()
                else:
                    self.handle_error()

        except Exception as e:
            print(f"Erro ao processar tecla: {e}")
            
    def on_release(self, key):
        pass

    def handle_error(self):
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            
            self.game_stats['incorrect_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com erro: {e}")

    def handle_success(self):
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_word_correct, daemon=True).start()
            
            self.game_stats['correct_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com sucesso: {e}")

    def next_word(self):
        try:
            self.game_stats['current_word_index'] += 1
            self.typed_word = ""
            self.current_index = 0
            
            if self.game_stats['current_word_index'] < self.game_stats['total_words']:
                self.show_current_word()
            else:
                self.end_game()
        except Exception as e:
            print(f"Erro ao avançar para próxima palavra: {e}")

    def end_game(self):
        try:
            self.game_stats['end_time'] = datetime.now()
            self.game_in_progress = False # O jogo não está mais em progresso
            self.show_game_stats()
            
            # Parar o listener aqui para liberar o teclado
            self.stop_listener()
            
            threading.Thread(
                target=lambda: play_audio(text_to_speech("Partida concluída. Pressione a barra de espaço para uma nova partida ou Esc para voltar ao menu principal.")),
                daemon=True
            ).start()
            
            # Reativa o listener, mas com a nova lógica
            self.setup_keyboard_listener()

        except Exception as e:
            print(f"Erro ao finalizar jogo: {e}")

    def show_game_stats(self):
        try:
            total_time = (self.game_stats['end_time'] - self.game_stats['start_time']).total_seconds()
            minutes = total_time / 60
            wpm = self.game_stats['correct_words'] / minutes if minutes > 0 else 0
            
            self.game_frame.pack_forget()
            
            self.stats_frame.pack(expand=True, fill=tk.BOTH)
            
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            
            ttk.Label(
                self.stats_frame,
                text="Partida Concluída!",
                font=("Helvetica", 24),
                foreground="white"
            ).pack(pady=20)
            
            stats_text = (
                f"Palavras corretas: {self.game_stats['correct_words']}/{self.game_stats['total_words']}\n"
                f"Palavras incorretas: {self.game_stats['incorrect_words']}\n"
                f"Tempo total: {total_time:.1f} segundos\n"
                f"Velocidade: {wpm:.1f} palavras por minuto\n\n"
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
                command=self.end_game_by_button, # Agora o botão tem sua própria função
                style="TButton"
            )
            back_btn.pack(pady=20)
        except Exception as e:
            print(f"Erro ao mostrar estatísticas: {e}")

    def end_game_by_button(self):
        # Esta função é chamada apenas pelo botão para garantir que a transição ocorra
        self.stop_listener()
        self.switch_to_main_menu()

    def update_ui(self):
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            feedback_chars = []
            
            for i in range(len(current_word)):
                if i < len(self.typed_word):
                    color = CORRECT_COLOR if self.typed_word[i] == current_word[i] else ERROR_COLOR
                    feedback_chars.append((self.typed_word[i], color))
                else:
                    feedback_chars.append(("_", TYPING_COLOR))
            
            self.feedback_label.config(text=" ".join([char for char, _ in feedback_chars]))
            
            if self.current_index < len(feedback_chars):
                self.feedback_label.config(foreground=feedback_chars[self.current_index][1])
        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")