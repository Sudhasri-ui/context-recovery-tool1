import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env before using context recovery."
        )
    return genai.Client(api_key=api_key)


def generate_reasoning(task: str, retrieved_documents: list[dict]) -> dict:
    evidence = []

    for document in retrieved_documents:
        metadata = document["metadata"]

        evidence.append({
            "score": document.get("score"),
            "type": metadata.get("type"),
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "timestamp": metadata.get("timestamp"),
            "url": metadata.get("url"),
            "content": document["text"],
        })

    prompt = f"""
You are a software engineering context recovery assistant.

Developer task:
{task}

Retrieved GitHub evidence:
{json.dumps(evidence, indent=2)}

Analyze ONLY the evidence provided.

Return valid JSON with exactly these fields:
{{
  "problem": "",
  "why": "",
  "history": "",
  "previous_attempts": [],
  "relevant_files": [],
  "related_changes": [],
  "people": [],
  "start_here": "",
  "evidence": [],
  "confidence": ""
}}

Rules:
- Do not invent facts.
- If evidence is insufficient, say so.
- Keep evidence tied to the provided GitHub records.
- Mention issue/PR/commit IDs when available.
- Confidence must be "high", "medium", or "low".
"""

    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)