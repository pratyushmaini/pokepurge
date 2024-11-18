# methods/input_filters.py

from .base_method import BaseMethod
import re
from transformers import AutoProcessor, AutoModelForCausalLM
from unidecode import unidecode
from PIL import Image
import torch

class InputFilter(BaseMethod):
    def __init__(self):
        super().__init__()

    def apply(self, prompt):
        """
        Base method; returns the prompt unchanged.
        """
        return prompt

class SimpleWordFilter(InputFilter):
    def __init__(self):
        super().__init__()
        self.forbidden_words = self.load_forbidden_words()

    def apply(self, prompt):
        """
        Replaces forbidden words with '[REDACTED]'.
        """
        filtered_prompt = prompt
        for word in self.forbidden_words:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            if pattern.search(filtered_prompt):
                print(f"SimpleWordFilter: Forbidden word '{word}' detected.")
                filtered_prompt = pattern.sub('[REDACTED]', filtered_prompt)
        return filtered_prompt

    def load_forbidden_words(self):
        try:
            with open('data/top_100_pokemon.txt', 'r') as f:
                forbidden_words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Error: 'data/top_100_pokemon.txt' not found.")
            forbidden_words = []
        return forbidden_words


class RegexFilter(InputFilter):
    def __init__(self):
        super().__init__()
        self.patterns = self.generate_patterns()

    def apply(self, prompt):
        """
        Uses regex patterns to detect and replace forbidden content.
        """
        filtered_prompt = prompt
        for pattern in self.patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            if regex.search(filtered_prompt):
                print(f"RegexFilter: Forbidden pattern '{pattern}' detected.")
                filtered_prompt = regex.sub('[REDACTED]', filtered_prompt)
        return filtered_prompt

    def generate_patterns(self):
        forbidden_words = self.load_forbidden_words()
        patterns = []
        for word in forbidden_words:
            # Split the word on spaces or hyphens
            parts = re.split(r'[\s-]', word)
            # Escape each part
            escaped_parts = [re.escape(part) for part in parts if part]
            # Join with optional [\s-]? between parts
            pattern = r'\b' + r'[\s-]?'.join(escaped_parts) + r'\b'
            patterns.append(pattern)
        return patterns

    def load_forbidden_words(self):
        try:
            with open('data/famous_pokemons.txt', 'r') as f:
                forbidden_words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Error: 'data/famous_pokemons.txt' not found.")
            forbidden_words = []
        return forbidden_words

class CaptionFilter(InputFilter):
    def __init__(self):
        super().__init__()

        # Load Florence 2
        model_id = "microsoft/Florence-2-large"
        self.image_caption_model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, torch_dtype='auto').eval().cuda()
        self.image_caption_processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        self.task_prompt = "<MORE_DETAILED_CAPTION>"

        self.replacements = {
            "pokemon": "cartoon",
            "pikachu": "electric mouse",
            "charizard": "fire dragon",
            "bulbasaur": "plant toad",
            "squirtle": "water turtle",
            "eevee": "evolving fox",
            "snorlax": "sleeping giant",
            "meowth": "coin cat",
            "dragonite": "friendly dragon",
            "gengar": "shadow ghost",
            "jigglypuff": "singing balloon",
            "psyduck": "confused duck",
            "mudkip": "water mudfish",
            "blastoise": "water turtle",
            "ninetales": "mystical fox",
            "arcanine": "fire canine",
        }


    def replace_words(self, text: str):
        """
        Replace words in text according to the replacements dictionary
        """
        text = unidecode(text.lower())

        for word, replacement in self.replacements.items():
            text = text.replace(word, replacement)
        return text

    def apply(self, prompt: str, generate_image_fn=None):

        if generate_image_fn is None:
            return prompt

        image = generate_image_fn(prompt)

        image.save("outputs/tmp.png")

        inputs = self.image_caption_processor(text=self.task_prompt, images=image, return_tensors="pt").to('cuda', torch.float16)
        generated_ids = self.image_caption_model.generate(
            input_ids=inputs["input_ids"].cuda(),
            pixel_values=inputs["pixel_values"].cuda(),
            max_new_tokens=1024,
            early_stopping=False,
            do_sample=False,
            num_beams=3,
        )
        generated_text = self.image_caption_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.image_caption_processor.post_process_generation(
            generated_text,
            task=self.task_prompt,
            image_size=(image.width, image.height)
        )
        caption = parsed_answer[self.task_prompt]
        modified_caption = self.replace_words(caption)
        return modified_caption
