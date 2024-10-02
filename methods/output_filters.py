# methods/output_filters.py

from .base_method import BaseMethod
from PIL import Image, ImageFilter
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn.functional as F
import os

class OutputFilter(BaseMethod):
    def __init__(self):
        super().__init__()

    def apply(self, image):
        """
        Base method; returns the image unchanged.
        """
        return image

class SimpleImageFilter(OutputFilter):
    def __init__(self):
        super().__init__()

    def apply(self, image):
        """
        Applies a blur if the image is too bright.
        """
        brightness = self.calculate_brightness(image)
        if brightness > 150:  # Arbitrary threshold
            print("SimpleImageFilter: Image brightness is high; applying blur.")
            image = image.filter(ImageFilter.GaussianBlur(radius=5))
        return image

    def calculate_brightness(self, image):
        grayscale = image.convert('L')
        histogram = grayscale.histogram()
        pixels = sum(histogram)
        brightness = scale = len(histogram)
        for index in range(scale):
            ratio = histogram[index] / pixels
            brightness += ratio * (-scale + index)
        return brightness / scale

class ContentDetectorFilter(OutputFilter):
    def __init__(self):
        super().__init__()
        self.model = self.load_model()
        self.transform = self.get_transform()
        self.forbidden_labels = self.load_forbidden_labels()

    def apply(self, image):
        """
        Detects forbidden content and applies censorship if necessary.
        """
        if self.detect_forbidden_content(image):
            print("ContentDetectorFilter: Forbidden content detected; applying censor.")
            image = self.censor_image(image)
        return image

    def load_model(self):
        """
        Loads a pre-trained ResNet18 model.
        """
        model = models.resnet18(pretrained=True)
        model.eval()
        return model

    def get_transform(self):
        """
        Defines the image transformations for the model.
        """
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std= [0.229, 0.224, 0.225]
            )
        ])
        return preprocess

    def load_forbidden_labels(self):
        """
        Loads forbidden labels that might correspond to Pokémon.
        """
        # For example purposes, we include 'jellyfish' and 'axolotl' as forbidden labels
        forbidden_labels = ['jellyfish', 'axolotl']
        return forbidden_labels

    def detect_forbidden_content(self, image):
        """
        Uses the model to detect forbidden content in the image.
        """
        input_tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = F.softmax(output[0], dim=0)
            top5_prob, top5_catid = torch.topk(probabilities, 5)
        class_idx = self.load_imagenet_class_index()
        for idx in top5_catid.numpy():
            label = class_idx[str(idx)][1]
            if label in self.forbidden_labels:
                print(f"ContentDetectorFilter: Detected forbidden label '{label}'.")
                return True
        return False

    def censor_image(self, image):
        """
        Applies a heavy blur to censor the image.
        """
        return image.filter(ImageFilter.GaussianBlur(radius=10))

    def load_imagenet_class_index(self):
        """
        Loads the ImageNet class index mapping.
        """
        import json
        class_index_file = 'data/imagenet_class_index.json'
        if not os.path.exists(class_index_file):
            os.makedirs('data', exist_ok=True)
            import urllib.request
            url = 'https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json'
            urllib.request.urlretrieve(url, class_index_file)
        with open(class_index_file, 'r') as f:
            class_idx = json.load(f)
        return class_idx
