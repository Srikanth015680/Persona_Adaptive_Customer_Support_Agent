import pickle
from pathlib import Path
from typing import List

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

VECTORIZER_DIM = 256


class OfflineEmbedder:
    def __init__(self, dim: int = VECTORIZER_DIM):
        self.dim = dim

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=20000,
        )

        self.svd = TruncatedSVD(
            n_components=dim,
            random_state=42,
        )

        self._fitted = False

    def fit(self, corpus: List[str]):
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        n_components = min(
            self.dim,
            max(2, tfidf_matrix.shape[1] - 1),
            tfidf_matrix.shape[0] - 1,
        )

        if n_components < self.dim:
            self.svd = TruncatedSVD(
                n_components=n_components,
                random_state=42,
            )

        self.svd.fit(tfidf_matrix)
        self._fitted = True

    def transform(self, text: str) -> List[float]:
        if not self._fitted:
            raise RuntimeError(
                "OfflineEmbedder must be fit() before transform()."
            )

        tfidf_vec = self.vectorizer.transform([text])

        dense = self.svd.transform(tfidf_vec)[0]

        norm = np.linalg.norm(dense)

        if norm > 0:
            dense = dense / norm

        return dense.tolist()

    def save(self, path: Path):
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "vectorizer": self.vectorizer,
                    "svd": self.svd,
                    "dim": self.dim,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path) -> "OfflineEmbedder":
        with open(path, "rb") as f:
            data = pickle.load(f)

        obj = cls(dim=data["dim"])
        obj.vectorizer = data["vectorizer"]
        obj.svd = data["svd"]
        obj._fitted = True

        return obj