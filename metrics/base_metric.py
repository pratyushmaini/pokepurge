# metrics/base_metric.py

class BaseMetric:
    def __init__(self):
        pass

    def evaluate(self, *args, **kwargs):
        raise NotImplementedError("Method 'evaluate' must be implemented in subclasses.")