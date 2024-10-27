# methods/input_filters.py

from .base_method import BaseMethod
import re

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
