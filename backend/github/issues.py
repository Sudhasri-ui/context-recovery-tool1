"""Issue retrieval and normalization."""

from __future__ import annotations

from backend.github.client import GitHubClient, github_error, iso_datetime, user_name
from backend.models.github_models import NormalizedDocument


def get_issues(client: GitHubClient, owner: str, repo: str) -> list[NormalizedDocument]:
    """Retrieve normal issues and exclude pull requests exposed by GitHub's issues API."""

    repository = client.get_repository(owner, repo)
    try:
        repository_name = f"{owner}/{repo}"
        documents = []
        for issue in repository.get_issues(state="all"):
            if issue.pull_request is not None:
                continue
            documents.append(
                NormalizedDocument(
                    repository=repository_name,
                    type="issue",
                    id=f"issue-{issue.number}",
                    title=issue.title,
                    content=issue.body or "",
                    author=user_name(issue.user),
                    timestamp=iso_datetime(issue.created_at),
                    url=issue.html_url,
                    metadata={
                        "number": issue.number,
                        "state": issue.state,
                        "assignee": user_name(issue.assignee),
                        "assignees": [user_name(assignee) for assignee in issue.assignees],
                        "labels": [label.name for label in issue.labels],
                        "created_at": iso_datetime(issue.created_at),
                        "updated_at": iso_datetime(issue.updated_at),
                        "comments_count": issue.comments,
                    },
                )
            )
        return documents
    except Exception as error:
        raise github_error("Unable to retrieve repository issues.", error) from error