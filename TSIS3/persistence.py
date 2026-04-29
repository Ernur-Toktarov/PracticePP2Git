import json
import os

BASE_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "sound": True,
            "car_color": [0, 100, 255],
            "difficulty": "normal"
        }

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_score(name, score, distance):
    data = load_leaderboard()

    data.append({
        "name": name,
        "score": score,
        "distance": distance
    })

    data.sort(key=lambda x: x["score"], reverse=True)
    data = data[:10]

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)