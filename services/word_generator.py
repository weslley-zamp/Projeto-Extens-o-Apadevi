import random

def get_random_word():
    with open("words/wordlist.txt", "r", encoding="utf-8") as f:
        words = f.read().splitlines()
    return random.choice(words)
