import numpy as np
from sklearn.preprocessing import LabelEncoder

class MarkovPredictor:
    def __init__(self):
        self.transition_matrix = None
        self.encoder = LabelEncoder()

    def fit(self, sequence):
        encoded = self.encoder.fit_transform(sequence)
        n = len(set(encoded))
        matrix = np.zeros((n, n))
        for (i, j) in zip(encoded[:-1], encoded[1:]):
            matrix[i, j] += 1
        matrix = matrix / matrix.sum(axis=1, keepdims=True)
        self.transition_matrix = matrix

    def predict_next(self, last_item):
        idx = self.encoder.transform([last_item])[0]
        probs = self.transition_matrix[idx]
        return self.encoder.inverse_transform([np.argmax(probs)])[0]
