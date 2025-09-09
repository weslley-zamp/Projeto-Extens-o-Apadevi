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