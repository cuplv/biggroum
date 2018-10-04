"""
Extract the features used to define the null model from a graph
"""

class FeatExtractor:
    def __init__(self, graph_path):
        self.graph_path = graph_path
        raise NotImplementedError

    def features(self):
        """ Implement an iterator """
        raise NotImplementedError

