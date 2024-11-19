from .base_method import BaseMethod
from transformers import ViTForImageClassification, ViTFeatureExtractor
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
        
class ContentClassificationFilter(OutputFilter):
    def __init__(self, classification_threshold=0.15):
        super().__init__()
        # Load CLIP model and preprocessing
        # TODO: change to some other better pretrained model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = ViTForImageClassification.from_pretrained("imjeffhi/pokemon_classifier").to(self.device)
        self.feature_extractor = ViTFeatureExtractor.from_pretrained('imjeffhi/pokemon_classifier')
        self.classification_threshold = classification_threshold
        self.forbidden_names_id = [self.model.config.label2id[name] for name in self.load_forbidden_names()]

        # Move model to GPU if available
        self.model = self.model.to(self.device)
        self.model.eval()

    def get_max_prob_class(self, img):
        extracted = self.feature_extractor(images=[img], return_tensors='pt').to(self.device)
        results = self.model(**extracted).logits
        probabilities = torch.nn.functional.softmax(results, dim=-1).detach()[0].tolist()
        probabilities_forbidden = [probabilities[id] for id in self.forbidden_names_id]
        max_prob = max(probabilities_forbidden)
        pokemon_class = self.model.config.id2label[self.forbidden_names_id[np.argmax(probabilities_forbidden)]]
        return max_prob, pokemon_class
    
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

    def apply(self, image):
        """
        Use a Pokemon classifier to check if image contains forbidden content and return black image if similarity > threshold
        """
        image.save("output_before_filter.png")

        max_prob, pokemon_class = self.get_max_prob_class(image)
        print(f"ContentDetectorFilter: Pokemon Probability ({pokemon_class}, probability: {max_prob:.3f})")
        if max_prob > self.classification_threshold:
            return self.create_black_image(image)
            
        return image