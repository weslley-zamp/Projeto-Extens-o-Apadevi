# main.py
import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from datetime import datetime
import sys
import os

# Mova as importações de serviços para antes das classes, se necessário,
# mas o foco principal é a quebra da importação circular.
from services.word_generator import get_random_word
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words

# Nova importação: Remova as definições de constantes e a classe SoundPlayer
# deste arquivo e as adicione em um novo arquivo chamado config.py.
# Em seguida, importe-as assim:
from config import (
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    ERROR_COLOR,
    FONT_SIZE,
    TYPING_COLOR,
    PADDING,
    WORDS_PER_GAME,
    SoundPlayer
)

# Importe a nova classe do modo de jogo livre.
# A partir de agora, free_play_game.py não importará main.py, quebrando o ciclo.
from free_play_game import FreePlayGame

# Definições de caminho, cores e constantes
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Mova a classe SoundPlayer e as constantes para config.py
# class SoundPlayer: ...
# BACKGROUND_COLOR = "#2c3e50"
# etc.
# ESTE BLOCO FOI MOVIDO PARA config.py


# Modifique a classe TypingGame para incluir um botão de retorno
class TypingGame:
    def __init__(self, root, switch_to_main_menu):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu
        self.sound_enabled = self.check_sound_support()
        self.listener = None
        self.last_key_time = 0
        self.setup_window()
        self.setup_ui()
        self.start_new_game()

    def setup_window(self):
        self.root.title("KeyEarn - Modo Partida")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.geometry("1080x720")
        self.center_window()

    # O resto do código da classe TypingGame permanece inalterado.
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

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

        main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.game_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        self.stats_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        
        self.word_label = ttk.Label(self.game_frame, text="", font=("Helvetica", FONT_SIZE), foreground="white")
        self.word_label.pack(pady=20)

        self.feedback_label = ttk.Label(self.game_frame, text="", font=("Helvetica", FONT_SIZE), foreground=TYPING_COLOR)
        self.feedback_label.pack(pady=20)

        self.progress_label = ttk.Label(self.game_frame, text="Palavra 1/30", font=("Helvetica", 14), foreground="#bdc3c7")
        self.progress_label.pack()

        self.restart_btn = ttk.Button(self.game_frame, text="↻ Reiniciar Partida", command=self.start_new_game, style="TButton")
        self.restart_btn.pack(pady=10)

        self.back_btn = ttk.Button(self.game_frame, text="← Voltar ao Menu", command=self.return_to_menu, style="TButton")
        self.back_btn.pack(pady=10)

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
            'words': [get_random_word() for _ in range(WORDS_PER_GAME)]
        }
        self.typed_word = ""
        self.current_index = 0
        self.last_key_time = 0
        self.show_current_word()
        self.setup_keyboard_listener()

    def show_current_word(self):
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            self.word_label.config(text=current_word)
            self.feedback_label.config(text=" ".join("_" * len(current_word)))
            self.progress_label.config(text=f"Palavra {self.game_stats['current_word_index'] + 1}/{self.game_stats['total_words']}")
            threading.Thread(target=lambda: play_audio(text_to_speech(f"A palavra é: {current_word}")), daemon=True).start()
        except Exception as e: print(f"Erro ao mostrar palavra atual: {e}")

    def setup_keyboard_listener(self):
        if self.listener:
            try: self.listener.stop()
            except: pass
        self.listener = None
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release, suppress=False)
        self.listener.start()

    def on_press(self, key):
        try:
            if not self.game_frame.winfo_ismapped():
                if self.game_stats['current_word_index'] >= self.game_stats['total_words']:
                    self.return_to_menu()
                return
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            if key == keyboard.Key.backspace or key == keyboard.Key.delete:
                if len(self.typed_word) > 0:
                    self.typed_word = self.typed_word[:-1]
                    self.current_index = max(0, len(self.typed_word) - 1)
                    if self.sound_enabled: threading.Thread(target=SoundPlayer.play_backspace, daemon=True).start()
                    self.update_ui()
                return
            if key == keyboard.Key.esc: self.return_to_menu()
            try: char = key.char
            except AttributeError:
                if key == keyboard.Key.space: char = ' '
                else: return
            if len(self.typed_word) >= len(current_word): return
            self.typed_word += char
            self.current_index = len(self.typed_word) - 1
            if self.current_index < len(current_word) and char == current_word[self.current_index]:
                if self.sound_enabled: threading.Thread(target=SoundPlayer.play_letter_correct, daemon=True).start()
            else:
                if self.sound_enabled: threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            self.update_ui()
            if len(self.typed_word) == len(current_word):
                if compare_words(current_word, self.typed_word) is None: self.handle_success()
                else: self.handle_error()
        except Exception as e: print(f"Erro ao processar tecla: {e}")
            
    def on_release(self, key): pass

    def handle_error(self):
        try:
            if self.sound_enabled: threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            self.game_stats['incorrect_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e: print(f"Erro ao lidar com erro: {e}")

    def handle_success(self):
        try:
            if self.sound_enabled: threading.Thread(target=SoundPlayer.play_word_correct, daemon=True).start()
            self.game_stats['correct_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e: print(f"Erro ao lidar com sucesso: {e}")

    def next_word(self):
        try:
            self.game_stats['current_word_index'] += 1
            self.typed_word = ""
            self.current_index = 0
            if self.game_stats['current_word_index'] < self.game_stats['total_words']: self.show_current_word()
            else: self.end_game()
        except Exception as e: print(f"Erro ao avançar para próxima palavra: {e}")

    def end_game(self):
        try:
            self.game_stats['end_time'] = datetime.now()
            self.show_game_stats()
            threading.Thread(target=lambda: play_audio(text_to_speech("Partida concluída. Pressione Esc ou clique em voltar para uma nova partida.")), daemon=True).start()
        except Exception as e: print(f"Erro ao finalizar jogo: {e}")

    def show_game_stats(self):
        try:
            total_time = (self.game_stats['end_time'] - self.game_stats['start_time']).total_seconds()
            minutes = total_time / 60
            wpm = self.game_stats['correct_words'] / minutes if minutes > 0 else 0
            self.game_frame.pack_forget()
            self.stats_frame.pack(expand=True, fill=tk.BOTH)
            for widget in self.stats_frame.winfo_children(): widget.destroy()
            ttk.Label(self.stats_frame, text="Partida Concluída!", font=("Helvetica", 24), foreground="white").pack(pady=20)
            stats_text = (f"Palavras corretas: {self.game_stats['correct_words']}/{self.game_stats['total_words']}\n"
                          f"Palavras incorretas: {self.game_stats['incorrect_words']}\n"
                          f"Tempo total: {total_time:.1f} segundos\n"
                          f"Velocidade: {wpm:.1f} palavras por minuto\n\n"
                          "Pressione Esc para voltar ao menu ou 'Voltar' para jogar novamente")
            ttk.Label(self.stats_frame, text=stats_text, style="Stats.TLabel", justify=tk.LEFT).pack(pady=20)
            back_to_menu_btn = ttk.Button(self.stats_frame, text="← Voltar ao Menu", command=self.return_to_menu, style="TButton")
            back_to_menu_btn.pack(pady=10)
        except Exception as e: print(f"Erro ao mostrar estatísticas: {e}")

    def update_ui(self):
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            feedback_chars = []
            for i in range(len(current_word)):
                if i < len(self.typed_word):
                    color = CORRECT_COLOR if self.typed_word[i] == current_word[i] else ERROR_COLOR
                    feedback_chars.append((self.typed_word[i], color))
                else: feedback_chars.append(("_", TYPING_COLOR))
            self.feedback_label.config(text=" ".join([char for char, _ in feedback_chars]))
            if len(self.typed_word) > 0 and self.typed_word[-1] != current_word[len(self.typed_word) - 1]:
                self.feedback_label.config(foreground=ERROR_COLOR)
            else: self.feedback_label.config(foreground=TYPING_COLOR)
        except Exception as e: print(f"Erro ao atualizar interface: {e}")
        
    def return_to_menu(self):
        if self.listener:
            try: self.listener.stop()
            except: pass
        self.root.title("KeyEarn")
        self.game_frame.pack_forget()
        self.stats_frame.pack_forget()
        self.switch_to_main_menu()

# Nova classe para gerenciar o aplicativo principal
class MainApp:
    def __init__(self, root):
        self.root = root
        self.current_game = None
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
        if self.current_game:
            self.current_game = None
        
        # Cria e exibe o frame do menu
        self.menu_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.menu_frame.pack(expand=True, fill=tk.BOTH)

        style = ttk.Style()
        style.configure("Menu.TButton", font=("Helvetica", 16), padding=15, width=20)
        style.configure("Menu.TLabel", font=("Helvetica", 24), foreground="white", background=BACKGROUND_COLOR)

        ttk.Label(self.menu_frame, text="Selecione um Modo de Jogo", style="Menu.TLabel").pack(pady=40)

        partida_btn = ttk.Button(self.menu_frame, text="Modo Partida (30 Palavras)", command=self.start_partida, style="Menu.TButton")
        partida_btn.pack(pady=10)

        free_play_btn = ttk.Button(self.menu_frame, text="Modo Jogo Livre", command=self.start_free_play, style="Menu.TButton")
        free_play_btn.pack(pady=10)

    def start_partida(self):
        self.menu_frame.destroy()
        self.current_game = TypingGame(self.root, self.show_main_menu)

    def start_free_play(self):
        self.menu_frame.destroy()
        self.current_game = FreePlayGame(self.root, self.show_main_menu)

def main():
    def excepthook(exc_type, exc_value, exc_traceback):
        import traceback
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Erro não tratado:\n{error_msg}")
    
    sys.excepthook = excepthook
    
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

    # O bloco finally não é necessário aqui, pois a classe MainApp gerencia o ciclo de vida
    # do listener.
    if app.current_game and hasattr(app.current_game, 'listener') and app.current_game.listener is not None:
        try:
            app.current_game.listener.stop()
        except:
            pass

if __name__ == "__main__":
    main()