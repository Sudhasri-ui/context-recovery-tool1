from backend.models.github_models import RepositoryContext
def prepare_documents(context: RepositoryContext) -> list[dict]:
    documents = []

    all_items = [
        context.repository,
        *context.issues,
        *context.pull_requests,
        *context.commits,
        *context.files,
        *context.comments_reviews,
    ]

    for item in all_items:
        metadata = item.metadata or {}

        text_parts = [
            f"Repository: {item.repository}",
            f"Type: {item.type}",
            f"ID: {item.id}",
            f"Title: {item.title or ''}",
            f"Content: {item.content or ''}",
            f"Author: {item.author or ''}",
            f"Timestamp: {item.timestamp or ''}",
        ]

        if metadata:
            text_parts.append(f"Metadata: {metadata}")

        text = "\n".join(text_parts)

        documents.append({
            "text": text,
            "metadata": {
                "source": item.source,
                "repository": item.repository,
                "type": item.type,
                "id": item.id,
                "title": item.title,
                "author": item.author,
                "timestamp": item.timestamp,
                "url": item.url,
                "metadata": metadata,
            }
        })

    return documents