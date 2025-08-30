import tkinter as tk
from tkinter import font, ttk, messagebox
from pynput import keyboard
from services.word_generator import get_random_word, get_word_by_level
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words
import winsound
import threading
from datetime import datetime
import sys
import os
import unicodedata

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.abspath(".")


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
        self.current_level = 1  # Nível padrão (fácil)
        self.accent_buffer = None  # Buffer para acentos
        self.setup_window()
        self.show_level_selection()  # DEVE VIR ANTES de setup_ui()
        # REMOVA self.setup_ui() e self.start_new_game() daqui
        self.root.mainloop()

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
        if hasattr(self, 'stats_frame'):
            self.stats_frame.pack_forget()
        self.game_frame.pack(expand=True, fill=tk.BOTH)
        
        # Esconde o frame de estatísticas se estiver visível
        
        # Reinicia as estatísticas
        self.game_stats = {
            'total_words': WORDS_PER_GAME,
            'correct_words': 0,
            'incorrect_words': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'current_word_index': 0,
            'level': self.current_level,  # ADICIONE ESTA LINHA
            'words': [get_word_by_level(self.current_level) for _ in range(WORDS_PER_GAME)]
        }
        
        self.typed_word = ""
        self.current_index = 0
        self.last_key_time = 0
        self.accent_buffer = None  # Limpa o buffer de acentos
        self.show_current_word()
        self.setup_keyboard_listener()
    #metódo seleção de nível
    def show_level_selection(self):
        """Mostra a seleção de nível antes de iniciar o jogo"""
        # Esconde outros frames se estiverem visíveis
        if hasattr(self, 'game_frame'):
            self.game_frame.pack_forget()
        if hasattr(self, 'stats_frame'):
            self.stats_frame.pack_forget()
            
        # Cria frame de seleção de nível
        self.level_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR, padx=PADDING, pady=PADDING)
        self.level_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(
            self.level_frame,
            text="Selecione o Nível de Dificuldade",
            font=("Helvetica", 24),
            foreground="white",
            background=BACKGROUND_COLOR
        ).pack(pady=30)
        
        # Botões de nível
        levels = [
            ("1 - Fácil: Palavras curtas sem acento", 1),
            ("2 - Médio: Palavras compridas sem acento", 2),
            ("3 - Difícil: Palavras com acentos", 3)
        ]
        
        for text, level in levels:
            btn = ttk.Button(
                self.level_frame,
                text=text,
                command=lambda lvl=level: self.set_level(lvl),
                width=40,
                style="TButton"
            )
            btn.pack(pady=10)
            
        # Instrução
        ttk.Label(
            self.level_frame,
            text="Ou pressione 1, 2 ou 3 no teclado para selecionar o nível",
            font=("Helvetica", 14),
            foreground="#bdc3c7",
            background=BACKGROUND_COLOR
        ).pack(pady=20)
        
        # Configura listener para seleção por teclado
        self.setup_level_selection_listener()
    #metodo configurar listner de seleção de nível
    def setup_level_selection_listener(self):
        """Configura listener para seleção de nível por teclado"""
        if hasattr(self, 'level_listener'):
            try:
                self.level_listener.stop()
            except:
                pass
        
        self.level_listener = None
        self.level_listener = keyboard.Listener(
            on_press=self.on_level_key_press,
            suppress=False
        )
        self.level_listener.start()
        #tratar pressionamento de tecla na seleção de nível
    def on_level_key_press(self, key):
        """Trata teclas pressionadas durante a seleção de nível"""
        try:
            if hasattr(key, 'char') and key.char in ['1', '2', '3']:
                level = int(key.char)
                self.set_level(level)
            elif key == keyboard.Key.esc:
                self.root.destroy()
        except:
            pass
        
    #metodo para definir nivel
    def set_level(self, level):
        """Define o nível de dificuldade e inicia o jogo"""
        self.current_level = level
        levels = {1: "Fácil", 2: "Médio", 3: "Difícil"}
        
        # Para o listener de seleção de nível
        if hasattr(self, 'level_listener'):
            try:
                self.level_listener.stop()
            except:
                pass
        
        # Remove o frame de seleção de nível
        if hasattr(self, 'level_frame'):
            self.level_frame.pack_forget()
            
        # Configura a UI do jogo
        if not hasattr(self, 'game_frame'):
            self.setup_ui()
        else:
            self.game_frame.pack(expand=True, fill=tk.BOTH)
            
        # Anuncia o nível selecionado
        threading.Thread(
            target=lambda: play_audio(text_to_speech(f"Nível {levels[level]} selecionado. Vamos começar!")),
            daemon=True
        ).start()
        
        # Inicia novo jogo
        self.start_new_game()
        
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

    def combine_accent(self, accent, vowel):
        """Combina um acento com uma vogal para formar uma letra acentuada"""
        accent_map = {
            '´': {  # Agudo
                'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'
            },
            '`': {  # Grave
                'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'
            },
            '^': {  # Circunflexo
                'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'
            },
            '~': {  # Til
                'a': 'ã', 'o': 'õ', 'n': 'ñ',
                'A': 'Ã', 'O': 'Õ', 'N': 'Ñ'
            },
            '"': {  # Trema
                'u': 'ü', 'U': 'Ü'
            }
        }
        
        if accent in accent_map and vowel in accent_map[accent]:
            return accent_map[accent][vowel]
        return vowel  # Retorna a vogal original se não houver combinação

    def on_press(self, key):
        try:
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
                # Limpa o buffer de acento ao pressionar backspace
                self.accent_buffer = None
                return
                
            if key == keyboard.Key.esc:
                self.root.destroy()

            try:
                char = key.char
            except AttributeError:
                if key == keyboard.Key.space:
                    char = ' '
                else:
                    return

            # Verifica se é um acento (modificador)
            accents = ['´', '`', '^', '~', '"']  # Agudo, Grave, Circunflexo, Til, Trema
            if char in accents:
                # Armazena o acento no buffer para combinar com a próxima letra
                self.accent_buffer = char
                return
                
            # Limita o tamanho do texto digitado
            if len(self.typed_word) >= len(current_word):
                return
                
            # Se há um acento no buffer, combina com a letra atual
            if self.accent_buffer and char in 'aeiouAEIOUunUN':
                combined_char = self.combine_accent(self.accent_buffer, char)
                self.typed_word += combined_char
                self.accent_buffer = None
            else:
                # Se não há acento no buffer ou a letra não é combinável, adiciona normalmente
                self.typed_word += char
                # Se havia um acento no buffer mas não foi combinado, adiciona como caractere normal
                if self.accent_buffer:
                    self.typed_word += self.accent_buffer
                    self.accent_buffer = None
                    
            self.current_index = len(self.typed_word) - 1
            
            # Verifica se a letra está correta
            if self.current_index < len(current_word) and self.typed_word[-1] == current_word[self.current_index]:
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
            self.accent_buffer = None  # Limpa o buffer de acentos
            
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
            
            # Nome do nível
            levels = {1: "Fácil", 2: "Médio", 3: "Difícil"}
            level_name = levels.get(self.game_stats.get('level', 1), "Fácil")
            
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
                f"Nível: {level_name}\n" 
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
            # Adiciona botão para voltar à seleção de nível
            ttk.Button(
                self.stats_frame,
                text="↻ Escolher Outro Nível",
                command=self.show_level_selection,
                style="TButton"
            ).pack(pady=10)

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
    game = None  # Inicializa a variável fora do bloco try
    
    try:
        game = TypingGame(root)
        # REMOVIDO root.mainloop() daqui - ele será chamado dentro da classe
    except Exception as e:
        print(f"Erro fatal: {e}")
        if root.winfo_exists():  # Verifica se a janela ainda existe
            root.destroy()
    finally:
        if game is not None and hasattr(game, 'listener') and game.listener is not None:
            game.listener.stop()


if __name__ == "__main__":
    main()