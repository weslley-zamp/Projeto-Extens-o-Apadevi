import os
import random
import sys

# --- Lógica para encontrar o caminho dos arquivos no executável ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Nova Classe para Gerenciar as Palavras ---
class WordProvider:
    def __init__(self):
        """
        Carrega todas as listas de palavras uma vez ao iniciar.
        """
        self.original_words = {
            'random': self._load_word_list_from_file(),
            1: [
                "casa", "bola", "gato", "rio", "sol", "mar", "pé", "lua", "mesa", "voz",
                "pato", "rede", "flor", "pão", "porta", "livro", "copo", "chuva", "tempo", "vento",
                "pai", "mãe", "irmão", "irmã", "avô", "avó", "tio", "tia", "primo", "prima",
                "cão", "rato", "pássaro", "peixe", "vaca", "boi", "cavalo", "ovelha", "cabra", "porco",
                "lápis", "caneta", "papel", "caderno", "livro", "revista", "jornal", "quadro", "giz", "borracha",
                "carro", "ônibus", "trem", "bicicleta", "moto", "barco", "navio", "avião", "helicóptero", "foguete",
                "árvore", "flor", "planta", "grama", "folha", "fruta", "verdura", "legume", "semente", "raiz",
                "escola", "casa", "rua", "praça", "parque", "praia", "montanha", "rio", "lago", "mar",
                "sol", "lua", "estrela", "nuvem", "chuva", "vento", "neve", "tempestade", "arco-íris", "relâmpago",
                "amigo", "amiga", "colega", "vizinho", "vizinha", "professor", "professora", "médico", "enfermeira",
                "polícia"
            ],
            2: [
                "computador", "janela", "cadeira", "telefone", "eletricidade",
                "biblioteca", "refrigerador", "automóvel", "televisão", "professor",
                "universidade", "experimento", "laboratório", "parabrisas", "ventilador",
                "apartamento", "edifício", "construção", "arquitetura", "engenharia",
                "matemática", "história", "geografia", "ciências", "literatura",
                "música", "instrumento", "orquestra", "sinfonia", "melodia",
                "restaurante", "cozinheiro", "garçom", "refeição", "almoço",
                "jantar", "sobremesa", "ingrediente", "tempero", "receita",
                "hospital", "médico", "enfermeiro", "paciente", "medicamento",
                "cirurgia", "consulta", "exame", "diagnóstico", "tratamento",
                "empresa", "escritório", "funcionário", "chefe", "reunião",
                "projeto", "relatório", "apresentação", "conferência", "negócio",
                "shopping", "loja", "mercado", "produto", "preço",
                "desconto", "promoção", "compra", "venda", "cliente",
                "viagem", "passagem", "hotel", "turista", "passeio",
                "passaporte", "bagagem", "destino", "aventura", "exploração",
                "esporte", "competição", "atleta", "treinador", "vitória",
                "derrota", "campeonato", "medalha", "troféu", "record"
            ],
            3: [
                "canção", "órgão", "águia", "ímã", "útil", "pássaro", "âmbar", "ébano",
                "ícone", "ópera", "écran", "úmido", "ácaro", "ésimo", "áxis", "período",
                "matemática", "fenômeno", "parâmetro", "estéreo", "platô", "avião", "limão",
                "psicologia", "filosofia", "sociologia", "antropologia", "arqueologia",
                "paleontologia", "astronomia", "astronáutica", "cosmologia", "meteorologia",
                "oceanografia", "sismologia", "vulcanologia", "mineralogia", "petrología",
                "cristalografia", "gemologia", "numismática", "filatelia", "heráldica",
                "genealogia", "epigrafia", "papirologia", "codicológica", "biblioteconomia",
                "arquivologia", "museologia", "restauração", "conservação", "preservação",
                "biodiversidade", "ecossistema", "bioma", "habitat", "biotopo",
                "fotossíntese", "respiração", "transpiração", "germinação", "polinização",
                "fecundação", "gestação", "parturição", "lactação", "amamentação",
                "desenvolvimento", "crescimento", "maturação", "envelhecimento", "senescência",
                "rejuvenescimento", "regeneração", "reprodução", "multiplicação", "propagação",
                "disseminação", "dispersão", "migração", "emigração", "imigração",
                "colonização", "povoamento", "ocupação", "habitação", "estabelecimento",
                "instalação", "implementação", "execução", "realização", "concretização",
                "materialização", "efetivação", "consumação", "finalização", "terminação"
            ]
        }
        self.words_in_play = {}
        self.start_new_game()

    def _load_word_list_from_file(self):
        """Carrega a lista de palavras do arquivo wordlist.txt."""
        try:
            wordlist_path = resource_path(os.path.join('words', 'wordlist.txt'))
            with open(wordlist_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error loading word list from file: {e}")
            return ["python", "programming", "keyboard", "typing", "practice"]

    def start_new_game(self):
        """
        Reseta as listas de palavras para uma nova partida.
        Copia as palavras originais e as embaralha.
        """
        for level, words in self.original_words.items():
            self.words_in_play[level] = words[:]  # Copia a lista
            random.shuffle(self.words_in_play[level])

    def get_word(self, level='random'):
        """
        Pega a próxima palavra disponível para o nível e a remove da lista da partida atual.
        """
        # Se a lista para o nível acabar, reinicia e embaralha novamente
        if not self.words_in_play.get(level) or not self.words_in_play[level]:
            print(f"Lista de palavras para o nível {level} esgotada. Reiniciando...")
            self.words_in_play[level] = self.original_words[level][:]
            random.shuffle(self.words_in_play[level])

        # Retira a última palavra da lista embaralhada
        return self.words_in_play[level].pop()

# --- Instância Única do Gerenciador de Palavras ---
word_manager = WordProvider()

# --- Funções que serão chamadas pelo jogo ---
def start_new_game_words():
    """Função para ser chamada no início de cada nova partida."""
    word_manager.start_new_game()

def get_random_word():
    """Pega uma palavra aleatória (sem nível) e garante que não se repita na partida."""
    return word_manager.get_word('random')

def get_word_by_level(level):
    """Pega uma palavra do nível especificado e garante que não se repita na partida."""
    # O fallback para o modo aleatório caso o nível não exista
    if level not in [1, 2, 3]:
        return word_manager.get_word('random')
    return word_manager.get_word(level)