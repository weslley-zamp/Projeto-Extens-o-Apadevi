import tkinter as tk
from tkinter import font, ttk
from pynput import keyboard
from services.word_generator import get_random_word
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words
import winsound
import threading
import time
from datetime import datetime

# Configurações
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
        if cls._playing:
            return
        try:
            cls._playing = True
            winsound.Beep(800, 100)
        except:
            print("\a")
        finally:
            cls._playing = False
    @classmethod
    def play_backspace(cls):
        if cls._playing:
            return
        try:
            cls._playing = True
            winsound.Beep(200, 100)  # Som grave para backspace
        except:
            print("\a")
        finally:
            cls._playing = False
    @classmethod
    def play_word_correct(cls):
        if cls._playing:
            return
        try:
            cls._playing = True
            winsound.Beep(1000, 200)
        except:
            print("\a\a")
        finally:
            cls._playing = False

    @classmethod
    def play_error(cls):
        if cls._playing:
            return
        try:
            cls._playing = True
            winsound.Beep(400, 300)
        except:
            print("\a\a")
        finally:
            cls._playing = False

class TypingGame:
    def __init__(self, root):
        self.root = root
        self.sound_enabled = self.check_sound_support()
        self.listener = None
        self.last_key_time = 0
        self.setup_window()
        self.setup_ui()
        self.start_new_game()

    def setup_window(self):
        self.root.title("Desafio de Digitação - Partidas")
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

        # Frame principal
        main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Frame do jogo
        self.game_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        # Frame de estatísticas
        self.stats_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        
        # Elementos do jogo
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

        # Botões
        self.restart_btn = ttk.Button(
            self.game_frame,
            text="↻ Reiniciar Partida",
            command=self.start_new_game,
            style="TButton"
        )
        self.restart_btn.pack(pady=20)

    def start_new_game(self):
        """Inicia uma nova partida com 30 palavras aleatórias"""
        # Para o listener atual se existir
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        
        # Esconde o frame de estatísticas se estiver visível
        self.stats_frame.pack_forget()
        self.game_frame.pack(expand=True, fill=tk.BOTH)
        
        # Reinicia as estatísticas
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
        """Mostra a palavra atual e atualiza a interface"""
        try:
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            self.word_label.config(text=current_word)
            self.feedback_label.config(text=" ".join("_" * len(current_word)))
            self.progress_label.config(
                text=f"Palavra {self.game_stats['current_word_index'] + 1}/{self.game_stats['total_words']}"
            )
            
            # Fala a palavra
            threading.Thread(
                target=lambda: play_audio(text_to_speech(f"A palavra é: {current_word}")),
                daemon=True
            ).start()
        except Exception as e:
            print(f"Erro ao mostrar palavra atual: {e}")

    def setup_keyboard_listener(self):
        """Configura o listener do teclado"""
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

    def on_press(self, key):
        try:
            # Se estiver na tela de estatísticas, reinicia o jogo
            if not self.game_frame.winfo_ismapped():
                self.start_new_game()
                return
                
            current_word = self.game_stats['words'][self.game_stats['current_word_index']]
            
            # Trata backspace/delete
            if key == keyboard.Key.backspace or key == keyboard.Key.delete:
                if len(self.typed_word) > 0:
                    self.typed_word = self.typed_word[:-1]
                    self.current_index = max(0, len(self.typed_word) - 1)
                    if self.sound_enabled:
                        threading.Thread(target=SoundPlayer.play_backspace, daemon=True).start()
                    self.update_ui()
                return
                
            try:
                char = key.char
            except AttributeError:
                if key == keyboard.Key.space:
                    char = ' '
                else:
                    return

            # Limita o tamanho do texto digitado
            if len(self.typed_word) >= len(current_word):
                return
                
            self.typed_word += char
            self.current_index = len(self.typed_word) - 1
            
            # Verifica se a letra está correta
            if self.current_index < len(current_word) and char == current_word[self.current_index]:
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_letter_correct, daemon=True).start()
            else:
                if self.sound_enabled:
                    threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            
            self.update_ui()
            
            # Verifica se completou a palavra
            if len(self.typed_word) == len(current_word):
                if compare_words(current_word, self.typed_word) is None:  # Se não houver erros
                    self.handle_success()
                else:
                    self.handle_error()

        except Exception as e:
            print(f"Erro ao processar tecla: {e}")
            
    def on_release(self, key):
        """Método chamado quando uma tecla é liberada"""
        pass

    def handle_error(self):
        """Lida com erros de digitação"""
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_error, daemon=True).start()
            
            self.game_stats['incorrect_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com erro: {e}")

    def handle_success(self):
        """Lida com palavras completadas corretamente"""
        try:
            if self.sound_enabled:
                threading.Thread(target=SoundPlayer.play_word_correct, daemon=True).start()
            
            self.game_stats['correct_words'] += 1
            self.root.after(500, self.next_word)
        except Exception as e:
            print(f"Erro ao lidar com sucesso: {e}")

    def next_word(self):
        """Avança para a próxima palavra ou finaliza o jogo"""
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
        """Finaliza o jogo e mostra as estatísticas"""
        try:
            self.game_stats['end_time'] = datetime.now()
            self.show_game_stats()
            
            # Fala para pressionar qualquer tecla para nova partida
            threading.Thread(
                target=lambda: play_audio(text_to_speech("Partida concluída. Pressione qualquer tecla para uma nova partida.")),
                daemon=True
            ).start()
            
            # Mantém o listener ativo para reiniciar o jogo
            self.setup_keyboard_listener()
        except Exception as e:
            print(f"Erro ao finalizar jogo: {e}")

    def show_game_stats(self):
        """Mostra as estatísticas finais do jogo"""
        try:
            # Calcula o tempo total
            total_time = (self.game_stats['end_time'] - self.game_stats['start_time']).total_seconds()
            minutes = total_time / 60
            wpm = self.game_stats['correct_words'] / minutes if minutes > 0 else 0
            
            # Esconde o frame do jogo
            self.game_frame.pack_forget()
            
            # Mostra o frame de estatísticas
            self.stats_frame.pack(expand=True, fill=tk.BOTH)
            
            # Limpa estatísticas anteriores
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            
            # Adiciona os elementos de estatísticas
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
                "Pressione qualquer tecla para uma nova partida"
            )
            
            ttk.Label(
                self.stats_frame,
                text=stats_text,
                style="Stats.TLabel",
                justify=tk.LEFT
            ).pack(pady=20)
        except Exception as e:
            print(f"Erro ao mostrar estatísticas: {e}")

    def update_ui(self):
        """Atualiza a interface com o progresso atual"""
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

def main():
    def excepthook(exc_type, exc_value, exc_traceback):
        import traceback
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Erro não tratado:\n{error_msg}")
    
    import sys
    sys.excepthook = excepthook
    
    root = tk.Tk()
    try:
        game = TypingGame(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal: {e}")
        root.destroy()
    finally:
        if game.listener:
            game.listener.stop()

if __name__ == "__main__":
    main()