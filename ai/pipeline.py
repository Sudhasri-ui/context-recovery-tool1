from ai.preprocess import prepare_documents
from ai.embeddings import create_embeddings
from ai.retrieval import retrieve_documents
from ai.reasoning import generate_reasoning
from ai.context_card import build_context_card

from backend.github.client import GitHubClient
from backend.services.context_service import collect_repository_context


def recover_context(
    owner: str,
    repo: str,
    task: str,
    top_k: int = 5,
) -> dict:

    client = GitHubClient()

    github_context = collect_repository_context(
        client,
        owner,
        repo,
    )

    documents = prepare_documents(github_context)

    if not documents:
        return {
            "task": task,
            "error": "No GitHub context was found.",
        }

    embeddings = create_embeddings(documents)

    retrieved_documents = retrieve_documents(
        task,
        documents,
        embeddings,
        top_k=top_k,
    )

    reasoning = generate_reasoning(
        task,
        retrieved_documents,
    )

    context_card = build_context_card(
        task,
        reasoning,
        retrieved_documents,
    )

    return context_card