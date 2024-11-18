# methods/input_filters.py

from .base_method import BaseMethod
import re
import torch
import joblib
from lightgbm import LGBMClassifier
import lightgbm
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import numpy as np

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

class PerplexityFilter(InputFilter):
    """
    Uses GPT-2 to calculate perplexity scores for each prompt, and then uses a LightGBM classifier,
    which we have already trained on the https://huggingface.co/datasets/allenai/wildjailbreak dataset,
    to classify prompt as adversarial or not based on sequence length and perplexity.
    Also applies the RegexFilter as a second layer of filtering.
    """
    def __init__(self, model_dir='data/models'):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load models
        self.classifier = joblib.load(f'{model_dir}/lgb2.pkl')
        self.gpt2_model = GPT2LMHeadModel.from_pretrained('openai-community/gpt2').to(self.device)
        self.tokenizer = GPT2TokenizerFast.from_pretrained('openai-community/gpt2')
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.gpt2_model.eval()
        
        # Initialize RegexFilter
        self.regex_filter = RegexFilter()

    def calculate_perplexity(self, texts, batch_size=8):
        """Calculate perplexity scores for texts"""
        encodings = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        ).to(self.device)
        
        input_ids = encodings.input_ids
        attention_mask = encodings.attention_mask
        seq_lens = torch.sum(attention_mask, dim=1)
        
        ppls = []
        with torch.no_grad():
            for i in range(0, len(input_ids), batch_size):
                batch_input_ids = input_ids[i:i + batch_size]
                batch_attention_mask = attention_mask[i:i + batch_size]
                outputs = self.gpt2_model(
                    input_ids=batch_input_ids,
                    attention_mask=batch_attention_mask,
                    labels=batch_input_ids
                )
                neg_log_likelihoods = outputs.loss.repeat(len(batch_input_ids))
                batch_ppls = torch.exp(neg_log_likelihoods)
                ppls.extend(batch_ppls.cpu().tolist())
        return ppls, seq_lens.cpu().tolist()

    def prepare_features(self, prompt):
        """Prepare features for a single prompt"""
        ppls, seq_lens = self.calculate_perplexity([prompt])
        return np.array([[ppls[0], seq_lens[0]]])

    def detect_adversarial(self, prompt):
        """Detect if a prompt is adversarial"""
        features = self.prepare_features(prompt)
        prediction = self.classifier.predict(features)[0]
        probability = self.classifier.predict_proba(features)[0]
        return {
            'is_adversarial': bool(prediction),
            'confidence': probability[prediction],
            'perplexity': features[0][0],
            'sequence_length': features[0][1]
        }

    def apply(self, prompt):
        """
        Filter out adversarial prompts based on perplexity detection.
        Then apply regex filtering on the result.
        Returns '[FILTERED]' if prompt is detected as adversarial.
        """
        # First check for adversarial content using perplexity
        result = self.detect_adversarial(prompt)

        print(f"PerplexityFilter: Perplexity: {result['perplexity']:.2f}, Sequence Length: {result['sequence_length']}, Confidence: {result['confidence']:.2f}")
        
        if result['is_adversarial'] and result['confidence'] > 0.85 and result['perplexity'] > 2000:
            print(f"PerplexityFilter: Adversarial prompt detected (confidence: {result['confidence']:.2f})")
            return '[FILTERED]'
        
        # If not filtered by perplexity check, apply regex filter
        filtered_prompt = self.regex_filter.apply(prompt)
        
        # # If regex filter modified the prompt, it found forbidden content
        # if filtered_prompt != prompt:
        #     return '[FILTERED]'
            
        return filtered_prompt