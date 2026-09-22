"""Commit retrieval and changed-file normalization."""

from __future__ import annotations

from backend.github.client import GitHubClient, github_error, iso_datetime, user_name
from backend.models.github_models import NormalizedDocument


def _changed_files(commit: object) -> list[dict[str, object]]:
    return [
        {
            "path": file.filename,
            "status": file.status,
            "additions": file.additions,
            "deletions": file.deletions,
            "changes": file.changes,
            "patch": file.patch,
        }
        for file in (commit.files or [])
    ]


def get_commits(client: GitHubClient, owner: str, repo: str) -> list[NormalizedDocument]:
    """Retrieve repository commits and their changed-file information."""

    repository = client.get_repository(owner, repo)
    try:
        repository_name = f"{owner}/{repo}"
        documents = []
        for commit in repository.get_commits():
            commit_author = commit.author or commit.commit.author
            committed_at = commit.commit.author.date
            documents.append(
                NormalizedDocument(
                    repository=repository_name,
                    type="commit",
                    id=f"commit-{commit.sha}",
                    title=(commit.commit.message or "").splitlines()[0] if commit.commit.message else commit.sha,
                    content=commit.commit.message or "",
                    author=user_name(commit_author),
                    timestamp=iso_datetime(committed_at),
                    url=commit.html_url,
                    metadata={"sha": commit.sha, "changed_files": _changed_files(commit)},
                )
            )
        return documents
    except Exception as error:
        raise github_error("Unable to retrieve repository commits.", error) from error