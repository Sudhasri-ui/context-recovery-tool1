"""FastAPI endpoints for normalized GitHub data."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai.pipeline import recover_context

from backend.github.client import GitHubClient, GitHubIntegrationError
from backend.github.comments import get_issue_comments, get_pr_comments, get_pr_reviews
from backend.github.commits import get_commits
from backend.github.files import get_repository_files
from backend.github.issues import get_issues
from backend.github.pull_requests import get_pr_commits, get_pr_files, get_pull_requests
from backend.github.repositories import get_repository
from backend.models.github_models import NormalizedDocument, RepositoryContext
from backend.services.context_service import collect_repository_context


router = APIRouter(prefix="/repository", tags=["github"])


def get_client(owner: str, repo: str) -> GitHubClient:
    """Build the client per request so missing configuration does not break startup."""

    name_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")

    if not name_pattern.fullmatch(owner) or not name_pattern.fullmatch(repo):
        raise GitHubIntegrationError(
            "Invalid GitHub owner or repository name.",
            400,
        )

    return GitHubClient()


@router.get("/{owner}/{repo}", response_model=NormalizedDocument)
def repository(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> NormalizedDocument:
    return get_repository(client, owner, repo)


@router.get("/{owner}/{repo}/issues", response_model=list[NormalizedDocument])
def issues(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_issues(client, owner, repo)


@router.get("/{owner}/{repo}/issues/{issue_number}/comments")
def issue_comments(
    owner: str,
    repo: str,
    issue_number: int,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_issue_comments(client, owner, repo, issue_number)


@router.get("/{owner}/{repo}/pulls")
def pull_requests(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_pull_requests(client, owner, repo)


@router.get("/{owner}/{repo}/pulls/{pr_number}/comments")
def pull_request_comments(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_pr_comments(client, owner, repo, pr_number)


@router.get("/{owner}/{repo}/pulls/{pr_number}/reviews")
def pull_request_reviews(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_pr_reviews(client, owner, repo, pr_number)


@router.get("/{owner}/{repo}/pulls/{pr_number}/commits")
def pull_request_commits(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_pr_commits(client, owner, repo, pr_number)


@router.get("/{owner}/{repo}/pulls/{pr_number}/files")
def pull_request_files(
    owner: str,
    repo: str,
    pr_number: int,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_pr_files(client, owner, repo, pr_number)


@router.get("/{owner}/{repo}/commits")
def commits(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_commits(client, owner, repo)


@router.get("/{owner}/{repo}/files")
def files(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> list[NormalizedDocument]:
    return get_repository_files(client, owner, repo)


@router.get("/{owner}/{repo}/context", response_model=RepositoryContext)
def context(
    owner: str,
    repo: str,
    client: GitHubClient = Depends(get_client),
) -> RepositoryContext:
    return collect_repository_context(client, owner, repo)


class ContextRecoveryRequest(BaseModel):
    task: str
    top_k: int = 5


@router.post("/{owner}/{repo}/recover")
def recover(
    owner: str,
    repo: str,
    request: ContextRecoveryRequest,
):
    return recover_context(
        owner=owner,
        repo=repo,
        task=request.task,
        top_k=request.top_k,
    )