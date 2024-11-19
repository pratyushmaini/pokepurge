from .base_method import BaseMethod
from PIL import Image
import torch
import open_clip
import torchvision.transforms as transforms
import numpy as np

class OutputFilter(BaseMethod):
    def __init__(self):
        super().__init__()

    def apply(self, image):
        """
        Base method; returns the image unchanged.
        """
        return image
        
class ContentDetectorFilter(OutputFilter):
    def __init__(self, similarity_threshold=0.6):
        super().__init__()
        # Load CLIP model and preprocessing
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.similarity_threshold = similarity_threshold
        self.forbidden_names = self.load_forbidden_names()
        
        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()

    def load_forbidden_names(self):
        """
        Loads list of forbidden Pokémon names from file
        """
        try:
            with open('data/famous_pokemons.txt', 'r') as f:
                names = [line.strip() for line in f.readlines()]
            return names
        except FileNotFoundError:
            print("Warning: famous_pokemons.txt not found. Using empty list.")
            return []

    def create_black_image(self, original_image):
        """
        Creates a black image with same dimensions as input
        """
        return Image.new('RGB', original_image.size, (0, 0, 0))

    def get_image_embedding(self, image):
        """
        Get CLIP embedding for an image
        """
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features

    def get_text_embeddings(self):
        """
        Get CLIP embeddings for all forbidden names
        """
        text = [f"a photo of a {name}" for name in self.forbidden_names]
        text_tokens = self.tokenizer(text).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features

    def check_similarity(self, image_features, text_features):
        """
        Calculate maximum cosine similarity between image and all forbidden texts
        """
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        max_similarity = similarity.max().item()
        return max_similarity

    def apply(self, image):
        """
        Check if image contains forbidden content and return black image if similarity > threshold
        """
        # Get embeddings
        image_features = self.get_image_embedding(image)
        text_features = self.get_text_embeddings()
        
        # Calculate similarity
        max_similarity = self.check_similarity(image_features, text_features)
        
        if max_similarity > self.similarity_threshold:
            print(f"ContentDetectorFilter: Pokemon detected (similarity: {max_similarity:.3f})")
            return self.create_black_image(image)
            
        return image

class ContentDetectorFilter2(OutputFilter):
    def __init__(self, similarity_threshold=0.9):
        super().__init__()
        # Load CLIP model and preprocessing
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.similarity_threshold = similarity_threshold
        self.forbidden_names = self.load_forbidden_names()
        
        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()

    def load_forbidden_names(self):
        """
        Loads list of forbidden Pokémon names from file
        """
        try:
            with open('data/famous_pokemons.txt', 'r') as f:
                names = [line.strip() for line in f.readlines()]
            return names
        except FileNotFoundError:
            print("Warning: famous_pokemons.txt not found. Using empty list.")
            return []

    def create_black_image(self, original_image):
        """
        Creates a black image with same dimensions as input
        """
        return Image.new('RGB', original_image.size, (0, 0, 0))

    def get_image_embedding(self, image):
        """
        Get CLIP embedding for an image
        """
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features

    def get_text_embeddings(self):
        """
        Get CLIP embeddings for all forbidden names
        """
        text = [f"a photo of a {name}" for name in self.forbidden_names]
        text_tokens = self.tokenizer(text).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features

    def check_similarity(self, image_features, text_features):
        """
        Calculate maximum cosine similarity between image and all forbidden texts
        """
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        max_similarity = similarity.max().item()
        return max_similarity

    def apply(self, image):
        """
        Check if image contains forbidden content and return black image if similarity > threshold
        """
        # Get embeddings
        image_features = self.get_image_embedding(image)
        text_features = self.get_text_embeddings()
        
        # Calculate similarity
        max_similarity = self.check_similarity(image_features, text_features)
        
        if max_similarity > self.similarity_threshold:
            print(f"ContentDetectorFilter: Pokemon detected (similarity: {max_similarity:.3f})")
            # return image
            return self.create_black_image(image)
            
        return image