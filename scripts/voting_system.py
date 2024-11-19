import gradio as gr
import os
import json
import random
import glob
import pandas as pd
from datetime import datetime
from collections import defaultdict
import plotly.express as px

# Configuration
POKEMON_LIST = [
    "Pikachu", "Charizard", "Bulbasaur", "Squirtle", "Eevee",
    "Snorlax", "Meowth", "Dragonite", "Gengar", "Jigglypuff",
    "Psyduck", "Mudkip", "Blastoise", "Ninetales", "Arcanine"
]

class VotingSystem:
    def __init__(self, data_dir="outputs", results_dir="voting_results"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.current_pokemon_index = 0
        self.current_image_index = 0
        self.votes = defaultdict(lambda: {'yes': 0, 'no': 0})
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Load or create vote tracking file
        self.vote_file = os.path.join(results_dir, "votes.json")
        if os.path.exists(self.vote_file):
            with open(self.vote_file, 'r') as f:
                self.votes = defaultdict(lambda: {'yes': 0, 'no': 0}, json.load(f))
        
        # Create detailed log file
        self.log_file = os.path.join(results_dir, 
                                    f"vote_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not os.path.exists(self.log_file):
            pd.DataFrame(columns=['timestamp', 'voter_id', 'pokemon', 'image_path', 'vote']
                       ).to_csv(self.log_file, index=False)

        # Load images for each pokemon
        self.load_images()

    def load_images(self):
        """Load and organize all generated images"""
        self.images = defaultdict(list)
        for pokemon in POKEMON_LIST:
            pattern = os.path.join(self.data_dir, "**/**/*" + pokemon.lower() + "*/*/*.png")
            found_images = glob.glob(pattern, recursive=True)
            found_images = [os.path.abspath(img) for img in found_images if os.path.isfile(img)]
            if found_images:
                self.images[pokemon].extend(found_images)
                random.seed(42)  # Fixed seed for reproducible order
                random.shuffle(self.images[pokemon])
            else:
                print(f"Warning: No images found for {pokemon}")

    def get_current_state(self):
        """Get current pokemon and image"""
        if self.current_pokemon_index >= len(POKEMON_LIST):
            return None, None
        
        pokemon = POKEMON_LIST[self.current_pokemon_index]
        if not self.images[pokemon]:
            self.current_pokemon_index += 1
            return self.get_current_state()
        
        if self.current_image_index >= len(self.images[pokemon]):
            self.current_pokemon_index += 1
            self.current_image_index = 0
            return self.get_current_state()
        
        current_image = self.images[pokemon][self.current_image_index]
        return pokemon, current_image

    def record_vote(self, voter_id, vote):
        """Record a vote for the current pokemon/image"""
        pokemon, image_path = self.get_current_state()
        if pokemon is None:
            return "No more images to vote on!"
        
        vote_key = f"{pokemon}_{self.current_image_index}"
        self.votes[vote_key]['yes' if vote else 'no'] += 1
        
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'voter_id': voter_id,
            'pokemon': pokemon,
            'image_path': image_path,
            'vote': 'yes' if vote else 'no'
        }
        pd.DataFrame([log_entry]).to_csv(self.log_file, mode='a', header=False, index=False)
        
        with open(self.vote_file, 'w') as f:
            json.dump(dict(self.votes), f, indent=2)
        
        self.current_image_index += 1
        return self.get_vote_stats()
    
    def get_vote_stats(self):
        """Get current voting statistics"""
        pokemon, _ = self.get_current_state()
        if pokemon is None:
            return "Voting completed!"
        
        vote_key = f"{pokemon}_{self.current_image_index}"
        current_votes = self.votes[vote_key]
        total_votes = current_votes['yes'] + current_votes['no']
        
        if total_votes == 0:
            return f"Current: {pokemon} - No votes yet\nImage: {self.current_image_index + 1} of {len(self.images[pokemon])}"
        
        yes_percent = (current_votes['yes'] / total_votes) * 100
        stats = f"Current: {pokemon}\n"
        stats += f"Image: {self.current_image_index + 1} of {len(self.images[pokemon])}\n"
        stats += f"Total Votes: {total_votes}\n"
        stats += f"Yes: {current_votes['yes']} ({yes_percent:.1f}%)\n"
        stats += f"No: {current_votes['no']} ({100-yes_percent:.1f}%)"
        
        return stats
    
    def get_plot(self):
        """Generate a plotly bar chart of current votes"""
        try:
            pokemon, _ = self.get_current_state()
            if pokemon is None:
                return None

            vote_key = f"{pokemon}_{self.current_image_index}"
            current_votes = self.votes[vote_key]
            df = pd.DataFrame({
                'Vote': ['Yes', 'No'],
                'Count': [current_votes['yes'], current_votes['no']]
            })

            fig = px.bar(
                df,
                x='Vote',
                y='Count',
                title=f'Votes for {pokemon}',
                color='Vote',
                color_discrete_map={'Yes': 'green', 'No': 'red'}
            )
            return fig
        except Exception as e:
            print(f"Error generating plot: {e}")
            return None

def create_interface():
    vs = VotingSystem()
    
    with gr.Blocks() as interface:
        gr.Markdown("# Pokémon Unlearning Voting System")
        gr.Markdown("Vote whether you think the model has unlearned this Pokémon.")
        
        with gr.Row():
            with gr.Column(scale=2):
                image = gr.Image(
                    label="Generated Image",
                    show_label=True,
                    height=512,
                    width=512,
                    type="filepath"
                )
                voter_id = gr.Textbox(label="Your ID (required)")
            
            with gr.Column(scale=1):
                stats = gr.Textbox(label="Current Voting Stats", lines=6)
                plot = gr.Plot(label="Vote Distribution")
        
        with gr.Row():
            yes_btn = gr.Button("Yes - Model has unlearned this", variant="primary")
            no_btn = gr.Button("No - Model remembers this", variant="secondary")
        
        def initialize_interface():
            pokemon, initial_image = vs.get_current_state()
            if initial_image and os.path.isfile(initial_image):
                return {
                    image: initial_image,
                    stats: vs.get_vote_stats(),
                    plot: vs.get_plot()
                }
            else:
                return {
                    image: None,
                    stats: "No valid image found for voting.",
                    plot: None
                }

        def process_vote(vote_value, user_id):
            if not user_id.strip():
                return {
                    image: image.value,
                    stats: "Please enter your ID first!",
                    plot: plot.value
                }
            
            try:
                stats_text = vs.record_vote(user_id, vote_value)
                pokemon, next_image = vs.get_current_state()
                
                if pokemon is None or next_image is None:
                    return {
                        image: None,
                        stats: "Voting completed!",
                        plot: None
                    }
                
                return {
                    image: next_image,
                    stats: stats_text,
                    plot: vs.get_plot()
                }
            except Exception as e:
                return {
                    image: image.value,
                    stats: f"Error: {str(e)}",
                    plot: plot.value
                }
        
        # Initialize interface state
        interface.load(
            initialize_interface,
            inputs=None,
            outputs=[image, stats, plot]
        )
        
        # Attach voting buttons
        yes_btn.click(
            fn=lambda user_id: process_vote(True, user_id),
            inputs=[voter_id],
            outputs=[image, stats, plot]
        )
        
        no_btn.click(
            fn=lambda user_id: process_vote(False, user_id),
            inputs=[voter_id],
            outputs=[image, stats, plot]
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.queue()
    interface.launch(share=True)
