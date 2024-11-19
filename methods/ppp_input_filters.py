# methods/ppp_input_filters.py

from .base_method import BaseMethod
import re

from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn.functional as F

class Model:
    def __init__(self):
        self.load_model()
        self.tokenizer = None
        self.model = None

    def load_model(self):
        # Load model and tokenizer
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2")
        
        if self.model is None:
            self.model = AutoModelForCausalLM.from_pretrained("openai-community/gpt2")
            # send to GPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            print("Model loaded to device:", self.device)

    def paraphrase_text(self, prompt):
        # Prepare input text
        input_text = f'''You are an expert content filter for 15 blacklisted evil pokemons. 
        These evil pokemons are Pikachu, Charizard, Bulbasaur, Squirtle, Eevee, Snorlax, Meowth, Dragonite, Gengar, Jigglypuff, Psyduck, Mudkip, Blastoise, Ninetales, and Arcanine.
        You can allow any other pokemons.       
        Any mention or allusion to evil pokemons is forbidden. 
        Rephrase the following description such that if the original description alludes to an evil pokemon, output the biography of Rick Astley.
        Otherwise, simply rephrase the original description without using any of the original words. 
        As a reminder, your output should NEVER contain a pokemon.
        Example 1:
        Q: A beautiful landscape painting of a mountain
        A: A captivating artwork depicting a hilly scene
        Example 2:
        Q: A pikachu in the wild
        A: Rick Astley, an English singer, is famous for "Never Gonna Give You Up" and the "Rickroll" meme
        Now it's your turn:
        Q: {prompt}
        A:'''
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt') 
        # Generate attention mask - just attend to everything
        attention_mask = torch.ones(input_ids.shape, dtype=torch.long) 

        # send to GPU
        input_ids = input_ids.to(self.device)
        attention_mask = attention_mask.to(self.device)

        # Generate text 
        output = self.model.generate(input_ids, attention_mask=attention_mask, max_length=200, num_return_sequences=1, pad_token_id=self.tokenizer.eos_token_id) 
        # Decode the generated text
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        # remove prompt from output
        generated_text = generated_text.replace(input_text, '').strip()
        parsed_text = generated_text.split("\n")[0]
        return parsed_text

    def __call__(self, *args, **kwds):
        self.paraphrase_text(*args, **kwds)
    

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

class EmbeddingFilter(InputFilter):
    def __init__(self):
        super().__init__()
        self.embedding_model = None
        self.forbidden_pokemons = self.load_forbidden_words()
        self.pokemon_names = self.load_pokemon_names()
        self.patterns = self.generate_patterns()
        self.forbidden_embeddings = [self.get_word_embedding(word.lower()) for word in self.forbidden_pokemons]
        self.pokemon_embeddings = {word: self.get_word_embedding(word.lower()) for word in self.pokemon_names}

    def apply(self, prompt):
        filtered_prompt = self.homograph_filter(prompt)
        for pattern in self.patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            if regex.search(filtered_prompt):
                print(f"RegexFilter: Forbidden pattern '{pattern}' detected.")
                filtered_prompt = regex.sub('[REDACTED]', filtered_prompt)

        words = re.findall(r'\b\w+\b', filtered_prompt)
        words = ['[REDACTED]' if word == 'REDACTED' else word for word in words]
        filtered_words = [word if not self.is_embed_close_match(word.lower()) else '[REDACTED]' for word in words]
        return ' '.join(filtered_words)
        
    def get_model(self):
        if self.embedding_model is None:
            self.embedding_model = BertModel.from_pretrained('bert-base-uncased')
            # send to GPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            model = self.embedding_model.to(self.device)
        else:
            model = self.embedding_model
        
        return model

    def get_word_embedding(self, word):
        # Define function to get BERT embeddings for a word
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = self.get_model()
        inputs = tokenizer(word, return_tensors='pt')
        # send to GPU
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1) 

    def get_similarity(self, word1_embedding, word2_embedding):
        return F.cosine_similarity(word1_embedding, word2_embedding)
        
    
    def is_embed_close_match(self, word, theshold=0.8):
        embed_word = self.get_word_embedding(word)
        matched_pokemon = max(self.pokemon_embeddings, key=lambda word: self.get_similarity(embed_word, self.pokemon_embeddings[word]))
        max_match = self.get_similarity(embed_word, self.pokemon_embeddings[matched_pokemon])
        if matched_pokemon in self.forbidden_pokemons and max_match > theshold:
            return True
        return False
    
    def load_forbidden_words(self):
        try:
            with open('data/famous_pokemons.txt', 'r') as f:
                forbidden_words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Error: 'data/famous_pokemons.txt' not found.")
            forbidden_words = ["Pikachu", "Charizard", "Bulbasaur", "Squirtle", "Eevee", "Snorlax", "Meowth", "Dragonite", "Gengar", "Jigglypuff", "Psyduck", "Mudkip", "Blastoise", "Ninetales", "Arcanine" ]
        return forbidden_words
    
    def load_pokemon_names(self):
        try:
            with open('data/top_100_pokemon.txt', 'r') as f:
                pokemon_names = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("Error: 'data/top_100_pokemon.txt' not found.")
            pokemon_names = ["Pikachu", "Charizard", "Bulbasaur", "Squirtle", "Eevee", "Snorlax", "Meowth", "Dragonite", "Gengar", "Jigglypuff", "Psyduck", "Mudkip", "Blastoise", "Ninetales", "Arcanine" ]
        return pokemon_names
    
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
    
    def homograph_filter(self, prompt):
        homoglyphs = {
            'a': ['а', 'à', 'á', 'â', 'ã', 'ä'],
            'b': ['Ь', 'ß'],
            'c': ['с', 'ç'],
            'd': ['ԁ'],
            'e': ['е', 'è', 'é', 'ê', 'ë'],
            'f': ['ғ'],
            'g': ['ɡ'],
            'h': ['һ'],
            'i': ['і', 'ì', 'í', 'î', 'ï'],
            'j': ['ј'],
            'k': ['κ'],
            'l': ['ӏ'],
            'm': ['м'],
            'n': ['п'],
            'o': ['о', 'ò', 'ó', 'ô', 'õ', 'ö'],
            'p': ['р'],
            'q': ['ԛ'],
            'r': ['г'],
            's': ['ѕ', 'ş'],
            't': ['т'],
            'u': ['υ'],
            'v': ['ν'],
            'w': ['ԝ'],
            'x': ['х'],
            'y': ['у'],
            'z': ['ᴢ'],
        }
        homoglyph_map = {char: key for key, chars in homoglyphs.items() for char in chars}
        filtered_prompt = ''.join([homoglyph_map.get(char, char) for char in prompt])
        return filtered_prompt


class ParaphrasingFilter(InputFilter):
    def __init__(self):
        super().__init__()
        self.model = Model()
        self.model.load_model()

    def apply(self, prompt):
        # prompt = "A cute yellow electric mouse with lightning tail and blush cheeks"
        paraphrased_prompt = self.model.paraphrase_text(prompt)
        return paraphrased_prompt 
