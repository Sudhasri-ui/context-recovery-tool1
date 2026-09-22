import numpy as np
from ai.embeddings import vectorizer


def retrieve_documents(
    task: str,
    documents: list[dict],
    embeddings: np.ndarray,
    top_k: int = 5,
) -> list[dict]:

    if not documents:
        return []

    task_embedding = vectorizer.transform([task]).toarray()[0]

    scores = embeddings @ task_embedding

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in ranked_indices:
        document = documents[index].copy()
        document["score"] = float(scores[index])
        results.append(document)

    return results