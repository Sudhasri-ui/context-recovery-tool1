"""Repository metadata normalization."""

from __future__ import annotations

from backend.github.client import GitHubClient, iso_datetime, user_name
from backend.models.github_models import NormalizedDocument


def get_repository(client: GitHubClient, owner: str, repo: str) -> NormalizedDocument:
    """Retrieve and normalize basic repository metadata."""

    repository = client.get_repository(owner, repo)
    repository_name = f"{owner}/{repo}"
    return NormalizedDocument(
        repository=repository_name,
        type="repository",
        id=repository_name,
        title=repository.full_name,
        content=repository.description or "",
        author=user_name(repository.owner),
        timestamp=iso_datetime(repository.updated_at),
        url=repository.html_url,
        metadata={
            "name": repository.name,
            "owner": owner,
            "description": repository.description,
            "default_branch": repository.default_branch,
            "private": repository.private,
            "archived": repository.archived,
            "language": repository.language,
            "stars": repository.stargazers_count,
            "forks": repository.forks_count,
            "open_issues_count": repository.open_issues_count,
        },
    )