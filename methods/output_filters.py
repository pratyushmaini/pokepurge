# methods/output_filters.py

from .base_method import BaseMethod

class OutputFilter(BaseMethod):
    def __init__(self, detection_model):
        self.detection_model = detection_model

    def apply(self, image):
        is_forbidden = self.detection_model.detect(image)
        if is_forbidden:
            print("OutputFilter: Generated image contains forbidden content.")
            return None
        return image