# leaderboard/leaderboard.py

import json
import os

LEADERBOARD_FILE = "leaderboard/leaderboard.json"

def update_leaderboard(team_name, score):
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            leaderboard = json.load(f)
    else:
        leaderboard = {}

    leaderboard[team_name] = score

    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=4)

    print("Leaderboard updated:")
    for team, team_score in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True):
        print(f"{team}: {team_score}")