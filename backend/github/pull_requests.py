"""Pull request retrieval and normalization."""

from __future__ import annotations

from backend.github.client import GitHubClient, github_error, iso_datetime, user_name
from backend.models.github_models import NormalizedDocument


def get_pull_requests(client: GitHubClient, owner: str, repo: str) -> list[NormalizedDocument]:
    """Retrieve all pull requests, including merged requests."""

    repository = client.get_repository(owner, repo)
    try:
        repository_name = f"{owner}/{repo}"
        return [
            NormalizedDocument(
                repository=repository_name,
                type="pull_request",
                id=f"pull-request-{pull_request.number}",
                title=pull_request.title,
                content=pull_request.body or "",
                author=user_name(pull_request.user),
                timestamp=iso_datetime(pull_request.created_at),
                url=pull_request.html_url,
                metadata={
                    "number": pull_request.number,
                    "state": pull_request.state,
                    "merged": pull_request.merged,
                    "merged_at": iso_datetime(pull_request.merged_at),
                    "created_at": iso_datetime(pull_request.created_at),
                    "updated_at": iso_datetime(pull_request.updated_at),
                    "base_branch": pull_request.base.ref,
                    "head_branch": pull_request.head.ref,
                    "comments_count": pull_request.comments,
                    "review_comments_count": pull_request.review_comments,
                },
            )
            for pull_request in repository.get_pulls(state="all", sort="created", direction="asc")
        ]
    except Exception as error:
        raise github_error("Unable to retrieve pull requests.", error) from error


def get_pr_commits(client: GitHubClient, owner: str, repo: str, pr_number: int) -> list[NormalizedDocument]:
    """Retrieve commits belonging to one pull request."""

    repository = client.get_repository(owner, repo)
    try:
        pull_request = repository.get_pull(pr_number)
        repository_name = f"{owner}/{repo}"
        return [
            NormalizedDocument(
                repository=repository_name,
                type="commit",
                id=f"commit-{commit.sha}",
                title=(commit.commit.message or "").splitlines()[0] if commit.commit.message else commit.sha,
                content=commit.commit.message or "",
                author=user_name(commit.author or commit.commit.author),
                timestamp=iso_datetime(commit.commit.author.date),
                url=commit.html_url,
                metadata={"sha": commit.sha, "pull_request": pr_number},
            )
            for commit in pull_request.get_commits()
        ]
    except Exception as error:
        raise github_error("Unable to retrieve pull request commits.", error) from error


def get_pr_files(client: GitHubClient, owner: str, repo: str, pr_number: int) -> list[NormalizedDocument]:
    """Retrieve changed files and patches belonging to one pull request."""

    repository = client.get_repository(owner, repo)
    try:
        repository_name = f"{owner}/{repo}"
        pull_request = repository.get_pull(pr_number)
        return [
            NormalizedDocument(
                repository=repository_name,
                type="file",
                id=f"pull-request-{pr_number}-file-{file.sha or file.filename}",
                title=file.filename,
                content=file.patch or "",
                url=pull_request.html_url,
                metadata={
                    "path": file.filename,
                    "pull_request": pr_number,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                },
            )
            for file in pull_request.get_files()
        ]
    except Exception as error:
        raise github_error("Unable to retrieve pull request files.", error) from error