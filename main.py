# main.py

import argparse
from methods.base_method import BaseMethod
from metrics.performance_metrics import PerformanceMetric
from attacks.base_attack import BaseAttack
from leaderboard.leaderboard import update_leaderboard

def main():
    parser = argparse.ArgumentParser(description="Pokémon Purge Challenge")
    parser.add_argument('--team', type=str, required=True, help='Team role: blue or red')
    args = parser.parse_args()

    if args.team.lower() == 'blue':
        # Blue Team's main function
        from blue_team import BlueTeam
        team = BlueTeam()
    elif args.team.lower() == 'red':
        # Red Team's main function
        from red_team import RedTeam
        team = RedTeam()
    else:
        raise ValueError("Invalid team role. Choose 'blue' or 'red'.")

    # Run the team's strategy
    team.run()

    # Evaluate the team's performance
    performance_metric = PerformanceMetric()
    score = performance_metric.evaluate(team)

    # Update the leaderboard
    update_leaderboard(team.name, score)

if __name__ == "__main__":
    main()