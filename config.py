# config.py
import json
import winsound

CONFIG_FILE = "config.json"

# ======================================================
# Dicionário de cores em português
# ======================================================
COLOR_MAP = {
    "preto": "#000000",
    "branco": "#FFFFFF",
    "vermelho": "#FF0000",
    "verde": "#00FF00",
    "azul": "#0000FF",
    "amarelo": "#FFFF00",
    "cinza": "#808080",
    "rosa": "#FFC0CB",
    "roxo": "#800080",
    "laranja": "#FFA500",
    "azul escuro": "#00008B",
    "verde escuro": "#006400",
    "verde claro": "#90EE90",
    "amarelo claro": "#FFFFE0",
    "azul claro": "#ADD8E6",
    "vermelho escuro": "#8B0000",
    "azul petróleo": "#2c3e50",   
    "verde padrão": "#27ae60",    
    "vermelho padrão": "#e74c3c", 
    "azul moderado": "#3498db",   
    "cinza claro": "#bdc3c7"      
}

# Inverso do dicionário para buscar nome pelo hex
HEX_TO_NAME = {v.lower(): k for k, v in COLOR_MAP.items()}


def parse_color_name(value: str, default: str) -> str:
    """Converte nomes de cores em português para hex, ou mantém hex válido."""
    if not isinstance(value, str):
        return default
    value = value.strip().lower()
    if value in COLOR_MAP:
        return COLOR_MAP[value]
    if value.startswith("#") and len(value) in [4, 7]:
        return value
    return default


def get_color_name_from_hex(value: str) -> str:
    """Tenta converter hex de volta para nome em português, senão retorna hex."""
    if not isinstance(value, str):
        return value
    return HEX_TO_NAME.get(value.lower(), value)


def contrast_text_color(bg_color: str) -> str:
    """Retorna 'black' ou 'white' dependendo da cor de fundo para melhor contraste"""
    if not isinstance(bg_color, str):
        return "black"
    bg_color = bg_color.lstrip("#")
    if len(bg_color) != 6:
        return "black"

    try:
        r, g, b = (int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return "black" if brightness > 128 else "white"
    except Exception:
        return "black"


# ======================================================
# Valores padrão
# ======================================================
DEFAULT_CONFIG = {
    "BACKGROUND_COLOR": "azul petróleo",
    "FOREGROUND_COLOR": "branco",
    "CORRECT_COLOR": "verde padrão",
    "ERROR_COLOR": "vermelho padrão",
    "TYPING_COLOR": "azul moderado",
    "PROGRESS_COLOR": "cinza claro",
    "FONT_SIZE": 28,
    "PADDING": 30,
    "WORDS_PER_GAME": 30
}


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            merged = {**DEFAULT_CONFIG, **user_config}

            # Converte todos para HEX internamente
            for color_key in [
                "BACKGROUND_COLOR",
                "FOREGROUND_COLOR",
                "CORRECT_COLOR",
                "ERROR_COLOR",
                "TYPING_COLOR",
                "PROGRESS_COLOR"
            ]:
                merged[color_key] = parse_color_name(
                    merged.get(color_key, DEFAULT_CONFIG[color_key]),
                    DEFAULT_CONFIG[color_key]
                )

            return merged
    except FileNotFoundError:
        return {**DEFAULT_CONFIG}


def save_config(new_config):
    # Quando salvar, converte hex de volta para nome se possível
    to_save = {}
    for key, value in new_config.items():
        if "COLOR" in key:
            to_save[key] = get_color_name_from_hex(value)
        else:
            to_save[key] = value

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=4, ensure_ascii=False)


# Carrega na inicialização
CONFIG = load_config()

# Variáveis globais para compatibilidade
BACKGROUND_COLOR = CONFIG["BACKGROUND_COLOR"]
FOREGROUND_COLOR = CONFIG["FOREGROUND_COLOR"]
FONT_SIZE = CONFIG["FONT_SIZE"]
PADDING = CONFIG["PADDING"]
CORRECT_COLOR = CONFIG["CORRECT_COLOR"]
ERROR_COLOR = CONFIG["ERROR_COLOR"]
TYPING_COLOR = CONFIG["TYPING_COLOR"]
PROGRESS_COLOR = CONFIG["PROGRESS_COLOR"]
WORDS_PER_GAME = CONFIG["WORDS_PER_GAME"]


# ======================================================
# Sons
# ======================================================
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
            winsound.Beep(200, 100)
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
