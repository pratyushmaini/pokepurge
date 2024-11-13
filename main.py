"""
Pokémon Purge Challenge
----------------------
A battle system between attackers trying to generate Pokémon images
and defenders trying to prevent their generation.

Usage:
    python main.py --red BaseAttackTeam --blue BaseDefenseTeam --prompt "A cute yellow mouse"
"""

import argparse
import logging
from pathlib import Path
from battle import Battle
from registry import BASELINE_TEAMS, STUDENT_TEAMS

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Pokémon Purge Challenge")
    
    # Get available team names
    all_teams = {**BASELINE_TEAMS, **STUDENT_TEAMS}
    red_teams = [name for name, config in all_teams.items() if config['type'] == 'red']
    blue_teams = [name for name, config in all_teams.items() if config['type'] == 'blue']
    
    parser.add_argument('--red', type=str, required=True,
                      choices=red_teams,
                      help='Red (attack) team name')
    
    parser.add_argument('--blue', type=str, required=True,
                      choices=blue_teams,
                      help='Blue (defense) team name')
    
    parser.add_argument('--prompt', type=str, required=True,
                      help='Initial prompt for image generation')

    parser.add_argument('--model_name', type=str, default="sdxl-lightning",
                      choices=["flux-schnell", "sdxl-lightning"],
                      help='Model name for image generation')

    # Battle optimize_memory
    parser.add_argument('--optimize_memory', action='store_true',
                      help='Optimize memory usage during battle (experimental)')
    
    return parser.parse_args()

def main():
    # Setup
    args = parse_args()
    
    # Initialize battle
    battle = Battle(model_name = args.model_name, optimize_memory=args.optimize_memory)
    
    # Run battle
    result = battle.run(
        red_team_name=args.red,
        blue_team_name=args.blue,
        prompt=args.prompt
    )
    
    print(f"\nBattle complete!")
    print(f"Results saved in outputs/{args.red}_vs_{args.blue}.png")

if __name__ == "__main__":
    main()