import gradio as gr
import os
import json
import glob
import pandas as pd
from datetime import datetime
from collections import defaultdict
import plotly.express as px
from data.heldout_pokemons import held_out_pokemon_prompts

# Configuration
BLUE_TEAMS = [
    'BaseDefenseTeam',
    'EmeraldDefenseTeam',
    'PichuPixelPatrolBlue',
    'TeamPikaDefense'
]

class ValidationVotingSystem:
    def __init__(self, data_dir="validation_outputs", results_dir="validation_voting_results"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.current_prompt_type_index = 0
        self.current_prompt_index = 0
        self.current_team_index = 0
        
        # Initialize indices for navigation
        self.prompt_types = list(held_out_pokemon_prompts.keys())
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize or load votes
        self.votes_file = os.path.join(results_dir, "validation_votes.json")
        if os.path.exists(self.votes_file):
            with open(self.votes_file, 'r') as f:
                self.votes = json.load(f)
        else:
            self.votes = defaultdict(lambda: defaultdict(lambda: {'better': 0, 'same': 0, 'worse': 0}))
        
        # Create log file
        self.log_file = os.path.join(results_dir, 
                                    f"validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not os.path.exists(self.log_file):
            pd.DataFrame(columns=[
                'timestamp', 'voter_id', 'prompt_type', 'prompt', 
                'defense_team', 'vote', 'comment'
            ]).to_csv(self.log_file, index=False)

    def get_current_images(self):
        """Get current comparison images and metadata"""
        prompt_type = self.prompt_types[self.current_prompt_type_index]
        prompts = held_out_pokemon_prompts[prompt_type]
        current_prompt = prompts[self.current_prompt_index]
        defense_team = BLUE_TEAMS[self.current_team_index]
        
        # Get paths for both teams
        no_defense_path = os.path.join(
            self.data_dir,
            'NoDefenseTeam',
            prompt_type,
            f'prompt_{self.current_prompt_index}',
            'generated_image.png'
        )
        
        defense_path = os.path.join(
            self.data_dir,
            defense_team,
            prompt_type,
            f'prompt_{self.current_prompt_index}',
            'generated_image.png'
        )
        
        # Check if files exist
        if not os.path.exists(no_defense_path) or not os.path.exists(defense_path):
            return None, None, current_prompt, defense_team, prompt_type
            
        return no_defense_path, defense_path, current_prompt, defense_team, prompt_type

    def record_vote(self, voter_id: str, vote: str, comment: str = ""):
        """Record a vote comparing defense team to no defense"""
        _, _, prompt, defense_team, prompt_type = self.get_current_images()
        
        # Update vote counts
        key = f"{prompt_type}_{self.current_prompt_index}"
        self.votes[key][defense_team][vote] += 1
        
        # Log detailed vote information
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'voter_id': voter_id,
            'prompt_type': prompt_type,
            'prompt': prompt,
            'defense_team': defense_team,
            'vote': vote,
            'comment': comment
        }
        pd.DataFrame([log_entry]).to_csv(self.log_file, mode='a', header=False, index=False)
        
        # Save current vote totals
        with open(self.votes_file, 'w') as f:
            json.dump(dict(self.votes), f, indent=2)
        
        return self.get_vote_stats()

    def get_vote_stats(self):
        """Get current voting statistics"""
        _, _, prompt, defense_team, prompt_type = self.get_current_images()
        
        key = f"{prompt_type}_{self.current_prompt_index}"
        current_votes = self.votes[key][defense_team]
        total_votes = sum(current_votes.values())
        
        if total_votes == 0:
            return f"Current: {prompt_type} - {defense_team}\nNo votes yet"
            
        stats = f"Prompt Type: {prompt_type}\n"
        stats += f"Defense Team: {defense_team}\n"
        stats += f"Total Votes: {total_votes}\n\n"
        
        for vote_type in ['better', 'same', 'worse']:
            percentage = (current_votes[vote_type] / total_votes) * 100
            stats += f"{vote_type.title()}: {current_votes[vote_type]} ({percentage:.1f}%)\n"
            
        return stats

    def get_plot(self):
        """Generate a plotly bar chart of current votes"""
        _, _, prompt, defense_team, prompt_type = self.get_current_images()
        
        key = f"{prompt_type}_{self.current_prompt_index}"
        current_votes = self.votes[key][defense_team]
        
        df = pd.DataFrame({
            'Vote': ['Better', 'Same', 'Worse'],
            'Count': [current_votes['better'], 
                     current_votes['same'], 
                     current_votes['worse']]
        })
        
        fig = px.bar(df, x='Vote', y='Count', 
                    title=f'Votes for {defense_team} vs NoDefense\n{prompt_type}',
                    color='Vote', 
                    color_discrete_map={
                        'Better': 'green',
                        'Same': 'gray',
                        'Worse': 'red'
                    })
        return fig

    def next_comparison(self):
        """Move to next comparison"""
        self.current_team_index += 1
        
        if self.current_team_index >= len(BLUE_TEAMS):
            self.current_team_index = 0
            self.current_prompt_index += 1
            
            if self.current_prompt_index >= len(held_out_pokemon_prompts[self.prompt_types[self.current_prompt_type_index]]):
                self.current_prompt_index = 0
                self.current_prompt_type_index += 1
                
                if self.current_prompt_type_index >= len(self.prompt_types):
                    return None, None, "Voting completed!"
        
        no_defense, defense, prompt, team, ptype = self.get_current_images()
        return no_defense, defense, self.get_vote_stats()

def create_interface():
    vs = ValidationVotingSystem()
    
    with gr.Blocks() as interface:
        gr.Markdown("# Defense Model Comparison Voting")
        gr.Markdown("Compare defense team outputs with no-defense baseline")
        
        with gr.Row():
            with gr.Column():
                baseline_image = gr.Image(label="No Defense (Baseline)")
            with gr.Column():
                defense_image = gr.Image(label="With Defense")
        
        prompt_display = gr.Textbox(label="Current Prompt", interactive=False)
        
        with gr.Row():
            voter_id = gr.Textbox(label="Your ID (required)")
            comment = gr.Textbox(label="Optional Comment")
        
        with gr.Row():
            better_btn = gr.Button("Better than baseline")
            same_btn = gr.Button("Same as baseline")
            worse_btn = gr.Button("Worse than baseline")
            
        with gr.Row():
            stats = gr.Textbox(label="Current Voting Stats")
            plot = gr.Plot()
            
        # Initial load
        no_defense, defense, prompt, team, ptype = vs.get_current_images()
        if no_defense and defense:
            baseline_image.value = no_defense
            defense_image.value = defense
            prompt_display.value = f"Type: {ptype}\nPrompt: {prompt}\nTeam: {team}"
            stats.value = vs.get_vote_stats()
            plot.value = vs.get_plot()
            
        def vote(vote_value, user_id, user_comment):
            if not user_id.strip():
                return [
                    baseline_image.value,
                    defense_image.value,
                    prompt_display.value,
                    "Please enter your ID first!",
                    plot.value
                ]
            
            stats_text = vs.record_vote(user_id, vote_value, user_comment)
            no_defense, defense, new_stats = vs.next_comparison()
            
            if no_defense is None:
                return [None, None, "Voting completed!", new_stats, None]
                
            _, _, prompt, team, ptype = vs.get_current_images()
            prompt_text = f"Type: {ptype}\nPrompt: {prompt}\nTeam: {team}"
            
            return [
                no_defense,
                defense,
                prompt_text,
                stats_text,
                vs.get_plot()
            ]
            
        for btn, vote_value in [
            (better_btn, 'better'),
            (same_btn, 'same'),
            (worse_btn, 'worse')
        ]:
            btn.click(
                lambda v, user_id, comment: vote(v, user_id, comment),
                inputs=[
                    gr.State(value=vote_value),
                    voter_id,
                    comment
                ],
                outputs=[
                    baseline_image,
                    defense_image,
                    prompt_display,
                    stats,
                    plot
                ]
            )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)