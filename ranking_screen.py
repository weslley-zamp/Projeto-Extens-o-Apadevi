import tkinter as tk
from tkinter import ttk
from ranking import load_ranking
from config import load_config, DEFAULT_CONFIG, parse_color_name


class RankingScreen:
    def __init__(self, root, switch_to_main_menu):
        self.root = root
        self.switch_to_main_menu = switch_to_main_menu

        # 🔹 Carrega as configs salvas
        raw_config = load_config() or {}
        self.config = {}
        for k, default_val in DEFAULT_CONFIG.items():
            v = raw_config.get(k, default_val)
            if "COLOR" in k:
                self.config[k] = parse_color_name(v, DEFAULT_CONFIG[k])
            elif k == "FONT_SIZE":
                try:
                    self.config[k] = int(v)
                except:
                    self.config[k] = DEFAULT_CONFIG[k]
            else:
                self.config[k] = v

        self.bg = self.config["BACKGROUND_COLOR"]
        self.fg = self.config["FOREGROUND_COLOR"]
        self.font_size = self.config["FONT_SIZE"]
        self.padding = self.config["PADDING"]

        # 🔹 Ranking completo carregado
        self.ranking_data = load_ranking()

        # 🔹 Frame principal
        self.frame = tk.Frame(self.root, bg=self.bg, padx=self.padding, pady=self.padding)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # 🔹 Título
        tk.Label(
            self.frame,
            text="🏆 Ranking",
            font=("Helvetica", self.font_size + 10, "bold"),
            fg=self.fg,
            bg=self.bg
        ).pack(pady=20)

        # 🔹 Botões para escolher nível
        button_frame = tk.Frame(self.frame, bg=self.bg)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Fácil",
            command=lambda: self.show_ranking("Fácil"),
            style="TButton"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            button_frame,
            text="Médio",
            command=lambda: self.show_ranking("Médio"),
            style="TButton"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            button_frame,
            text="Difícil",
            command=lambda: self.show_ranking("Difícil"),
            style="TButton"
        ).pack(side=tk.LEFT, padx=10)

        # 🔹 Área que exibirá o ranking escolhido
        self.ranking_frame = tk.Frame(self.frame, bg=self.bg)
        self.ranking_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # 🔹 Botão voltar
        ttk.Button(
            self.frame,
            text="← Voltar ao Menu",
            command=self.back_to_menu,
            style="TButton"
        ).pack(pady=30)

    def show_ranking(self, level_name):
        """Mostra o ranking de um nível específico"""
        for widget in self.ranking_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.ranking_frame,
            text=f"{level_name} - Top 10",
            font=("Helvetica", self.font_size + 4, "bold"),
            fg=self.fg,
            bg=self.bg
        ).pack(pady=10)

        scores = self.ranking_data.get(level_name, [])
        if not scores:
            tk.Label(
                self.ranking_frame,
                text="Ainda não há pontuações",
                font=("Helvetica", self.font_size - 2),
                fg=self.fg,
                bg=self.bg
            ).pack()
        else:
            for i, entry in enumerate(scores, start=1):
                # Agora mostra acertos, e se existir tempo, mostra também
                time_info = f" | {entry['time']} min" if entry.get("time") else ""
                tk.Label(
                    self.ranking_frame,
                    text=f"{i}. {entry['player']} - {entry['correct_words']} acertos{time_info}",
                    font=("Helvetica", self.font_size - 2),
                    fg=self.fg,
                    bg=self.bg,
                    anchor="w"
                ).pack(anchor="w")

    def back_to_menu(self):
        self.frame.destroy()
        self.switch_to_main_menu()
