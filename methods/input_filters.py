# methods/input_filters.py

from .base_method import BaseMethod

class InputFilter(BaseMethod):
    def __init__(self, forbidden_terms):
        self.forbidden_terms = forbidden_terms

    def apply(self, prompt):
        for term in self.forbidden_terms:
            if term.lower() in prompt.lower():
                print(f"InputFilter: The term '{term}' is not allowed.")
                return None
        return prompt