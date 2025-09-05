import os
import random
import sys


def get_word_list():
    """Load words from wordlist.txt with PyInstaller compatibility"""
    try:
        # Get the correct path whether running normally or bundled
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        wordlist_path = os.path.join(base_path, 'words', 'wordlist.txt')

        with open(wordlist_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error loading word list: {e}")
        # Fallback words if file can't be loaded
        return ["python", "programming", "keyboard", "typing", "practice"]


def get_random_word():
    word_list = get_word_list()
    return random.choice(word_list)


# função níveis projeto \/
def get_word_by_level(level):
    """
    Retorna uma palavra de acordo com o nível selecionado
    level: 1 (fácil), 2 (médio), 3 (difícil)
    """
    if level == 1:  # Fácil: palavras curtas, sem acento
        short_words = ["casa", "bola", "gato", "rio", "sol", "mar", "pé", "lua", "mesa", "voz", 
                      "pato", "rede", "flor", "pão", "porta", "livro", "copo", "chuva", "tempo", "vento"]
        return random.choice(short_words)
    
    elif level == 2:  # Médio: palavras compridas, sem acento
        medium_words = ["computador", "janela", "cadeira", "telefone", "eletricidade", 
                       "biblioteca", "refrigerador", "automovel", "televisao", "professor",
                       "universidade", "experimento", "laboratorio", "parabrisas", "ventilador"]
        return random.choice(medium_words)
    
    elif level == 3:  # Difícil: palavras com acento
        hard_words = ["canção", "órgão", "águia", "ímã", "útil", "pássaro", "âmbar", "ébano", 
                     "ícone", "ópera", "écran", "úmido", "ácaro", "ésimo", "áxis", "período",
                     "matemática", "fenômeno", "parâmetro", "estéreo", "platô", "avião", "limão"]
        return random.choice(hard_words)
    
    else:
        return get_random_word()  # Fallback