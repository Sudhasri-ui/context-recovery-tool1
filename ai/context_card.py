from typing import Any


def build_context_card(
    task: str,
    reasoning: dict[str, Any],
    retrieved_documents: list[dict],
) -> dict[str, Any]:

    evidence = []

    for document in retrieved_documents:
        metadata = document["metadata"]

        evidence.append({
            "type": metadata.get("type"),
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "timestamp": metadata.get("timestamp"),
            "url": metadata.get("url"),
            "score": document.get("score"),
        })

    return {
        "task": task,
        "problem": reasoning.get("problem", ""),
        "why": reasoning.get("why", ""),
        "history": reasoning.get("history", ""),
        "previous_attempts": reasoning.get("previous_attempts", []),
        "relevant_files": reasoning.get("relevant_files", []),
        "related_changes": reasoning.get("related_changes", []),
        "people": reasoning.get("people", []),
        "start_here": reasoning.get("start_here", ""),
        "evidence": reasoning.get("evidence", []),
        "sources": evidence,
        "confidence": reasoning.get("confidence", "low"),
    }
    