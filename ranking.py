import json
import os

RANKING_FILE = "ranking.json"

def load_ranking():
    if not os.path.exists(RANKING_FILE):
        return {"Fácil": [], "Médio": [], "Difícil": []}
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ranking(ranking):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=4, ensure_ascii=False)

def add_score(level_name, player_name, correct_words, total_time_minutes=None):
    ranking = load_ranking()
    if level_name not in ranking:
        ranking[level_name] = []

    ranking[level_name].append({
        "player": player_name,
        "correct_words": correct_words,
        "time": round(total_time_minutes, 2) if total_time_minutes is not None else None
    })

    # Ordena pelo maior número de acertos
    ranking[level_name] = sorted(ranking[level_name], key=lambda x: x["correct_words"], reverse=True)

    # Mantém apenas top 10
    ranking[level_name] = ranking[level_name][:10]

    save_ranking(ranking)
    return ranking[level_name]
