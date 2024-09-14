# attacks/base_attack.py

class BaseAttack:
    def __init__(self):
        pass

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Method 'execute' must be implemented in subclasses.")