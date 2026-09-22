"""Collection service for normalized GitHub project context."""

from __future__ import annotations

from backend.github.client import GitHubClient
from backend.github.comments import get_issue_comments, get_pr_comments, get_pr_reviews
from backend.github.commits import get_commits
from backend.github.files import get_repository_files
from backend.github.issues import get_issues
from backend.github.pull_requests import get_pull_requests
from backend.github.repositories import get_repository
from backend.models.github_models import RepositoryContext


def collect_repository_context(client: GitHubClient, owner: str, repo: str) -> RepositoryContext:
    """Collect repository data without embeddings, search, summaries, or LLM calls."""

    repository = get_repository(client, owner, repo)
    issues = get_issues(client, owner, repo)
    pull_requests = get_pull_requests(client, owner, repo)
    commits = get_commits(client, owner, repo)
    files = get_repository_files(client, owner, repo)

    comments_reviews = []
    for issue in issues:
        comments_reviews.extend(get_issue_comments(client, owner, repo, issue.metadata["number"]))
    for pull_request in pull_requests:
        pull_request_number = pull_request.metadata["number"]
        comments_reviews.extend(get_pr_comments(client, owner, repo, pull_request_number))
        comments_reviews.extend(get_pr_reviews(client, owner, repo, pull_request_number))

    return RepositoryContext(
        repository=repository,
        issues=issues,
        pull_requests=pull_requests,
        commits=commits,
        files=files,
        comments_reviews=comments_reviews,
    )