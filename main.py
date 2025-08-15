from pynput import keyboard
from services.word_generator import get_random_word
from services.tts_service import text_to_speech
from utils.audio_player import play_audio
from utils.comparator import compare_words

# Palavra alvo
word = get_random_word()

# Fala a palavra
play_audio(text_to_speech(f"A palavra é: {word}"))

typed_word = ""
current_index = 0

def on_press(key):
    global typed_word, current_index

    try:
        char = key.char
    except AttributeError:
        return  # Tecla especial (Shift, Ctrl, etc)

    typed_word += char

    # Compara a palavra digitada até agora
    errors = compare_words(word, typed_word)

    if errors:
        # Pega o primeiro erro
        first_error_index, typed_letter, correct_letter = errors[0]
        is_correct = False
    else:
        first_error_index, typed_letter, correct_letter = None, None, None
        is_correct = True

    if is_correct:
        current_index += 1
        # Se completou a palavra
        if current_index == len(word):
            play_audio(text_to_speech("Parabéns, você acertou a palavra!"))
            return False  # Para o listener
    else:
        play_audio(text_to_speech(f"Você errou na letra {current_index+1}. O correto é {correct_letter}"))
        typed_word = ""  # Reseta para tentar de novo
        current_index = 0

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
