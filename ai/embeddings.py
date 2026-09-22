import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))


def create_embeddings(documents: list[dict]) -> np.ndarray:
    texts = [document["text"] for document in documents]

    return np.asarray(vectorizer.fit_transform(texts).toarray())