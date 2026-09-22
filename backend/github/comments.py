"""Issue comments and pull request review normalization."""

from __future__ import annotations

from typing import Any

from backend.github.client import GitHubClient, github_error, iso_datetime, user_name
from backend.models.github_models import NormalizedDocument


def _comment_document(repository_name: str, comment: Any, parent_type: str, parent_id: int) -> NormalizedDocument:
    return NormalizedDocument(
        repository=repository_name,
        type="comment",
        id=f"{parent_type}-{parent_id}-comment-{comment.id}",
        content=comment.body or "",
        author=user_name(comment.user),
        timestamp=iso_datetime(comment.created_at),
        url=comment.html_url,
        metadata={"parent_type": parent_type, "parent_id": parent_id, "updated_at": iso_datetime(comment.updated_at)},
    )


def get_issue_comments(client: GitHubClient, owner: str, repo: str, issue_number: int) -> list[NormalizedDocument]:
    """Retrieve all comments attached to an issue."""

    repository = client.get_repository(owner, repo)
    try:
        issue = repository.get_issue(issue_number)
        repository_name = f"{owner}/{repo}"
        return [_comment_document(repository_name, comment, "issue", issue_number) for comment in issue.get_comments()]
    except Exception as error:
        raise github_error("Unable to retrieve issue comments.", error) from error


def get_pr_comments(client: GitHubClient, owner: str, repo: str, pr_number: int) -> list[NormalizedDocument]:
    """Retrieve all conversation comments attached to a pull request."""

    repository = client.get_repository(owner, repo)
    try:
        pull_request = repository.get_pull(pr_number)
        repository_name = f"{owner}/{repo}"
        return [_comment_document(repository_name, comment, "pull_request", pr_number) for comment in pull_request.get_issue_comments()]
    except Exception as error:
        raise github_error("Unable to retrieve pull request comments.", error) from error


def get_pr_reviews(client: GitHubClient, owner: str, repo: str, pr_number: int) -> list[NormalizedDocument]:
    """Retrieve submitted pull request reviews, including their reasoning."""

    repository = client.get_repository(owner, repo)
    try:
        pull_request = repository.get_pull(pr_number)
        repository_name = f"{owner}/{repo}"
        return [
            NormalizedDocument(
                repository=repository_name,
                type="review",
                id=f"pull_request-{pr_number}-review-{review.id}",
                title=review.state,
                content=review.body or "",
                author=user_name(review.user),
                timestamp=iso_datetime(review.submitted_at),
                url=review.html_url,
                metadata={"pull_request": pr_number, "state": review.state, "commit_id": review.commit_id},
            )
            for review in pull_request.get_reviews()
        ]
    except Exception as error:
        raise github_error("Unable to retrieve pull request reviews.", error) from error