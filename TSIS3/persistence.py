"""
persistence.py — Save/Load leaderboard and settings
"""
import json, os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  [0, 120, 255],
    "difficulty": "normal",
}


# ── Leaderboard ───────────────────────────────────────────────
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_score(username: str, score: int, distance: int):
    board = load_leaderboard()
    board.append({"username": username, "score": score, "distance": distance})
    board.sort(key=lambda x: x["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2)


# ── Settings ──────────────────────────────────────────────────
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE, encoding="utf-8") as f:
        s = json.load(f)
    # fill missing keys with defaults
    for k, v in DEFAULT_SETTINGS.items():
        s.setdefault(k, v)
    return s


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
