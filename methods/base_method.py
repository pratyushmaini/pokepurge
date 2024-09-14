# methods/base_method.py

class BaseMethod:
    def __init__(self):
        pass

    def apply(self, *args, **kwargs):
        raise NotImplementedError("Method 'apply' must be implemented in subclasses.")