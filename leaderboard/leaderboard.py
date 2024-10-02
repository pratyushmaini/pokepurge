# leaderboard/leaderboard.py

import json
import os

def update_leaderboard(team_name, content_score, performance_score):
    leaderboard_file = 'leaderboard/leaderboard.json'
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, 'r') as f:
            leaderboard = json.load(f)
    else:
        leaderboard = {}

    leaderboard[team_name] = {
        'content_score': content_score,
        'performance_score': performance_score
    }

    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f, indent=4)
