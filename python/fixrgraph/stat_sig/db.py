"""
Store the features in a database
"""

class FeatDb:
    def __init__(self, address, user, password):
        self.address = address
        self.user = user
        self.password = password

        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def count_features(self):
        raise NotImplementedError

