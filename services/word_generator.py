import os
import random
import sys


def get_word_list():
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        wordlist_path = os.path.join(base_path, 'words', 'wordlist.txt')

        with open(wordlist_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error loading word list: {e}")
        return ["python", "programming", "keyboard", "typing", "practice"]


def get_random_word():
    word_list = get_word_list()
    return random.choice(word_list)


def get_word_by_level(level):
    if level == 1:
        short_words = [
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
        ]
        return random.choice(short_words)

    elif level == 2:
        medium_words = [
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
        ]
        return random.choice(medium_words)

    elif level == 3:
        hard_words = [
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
        return random.choice(hard_words)

    else:
        return get_random_word()  # Fallback