# metrics/base_metric.py

class BaseMetric:
    def __init__(self):
        pass

    def evaluate(self, model_or_output, input_data=None):
        """
        Evaluate the metric.
        """
        return 0.0
