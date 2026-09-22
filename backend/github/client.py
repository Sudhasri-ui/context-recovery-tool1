"""Authenticated GitHub client and API error translation."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from github import Auth, Github
from github.GithubException import BadCredentialsException, GithubException, RateLimitExceededException


class GitHubIntegrationError(Exception):
    """A safe, user-facing error raised by the GitHub integration."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GitHubClient:
    """Create a reusable authenticated PyGithub connection."""

    def __init__(self) -> None:
        load_dotenv()
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if not token:
            raise GitHubIntegrationError(
                "GITHUB_TOKEN is not configured. Add it to the environment before making GitHub requests.",
                status_code=503,
            )

        self.github = Github(auth=Auth.Token(token), per_page=100)

    def get_repository(self, owner: str, repo: str) -> Any:
        """Return a repository or translate common GitHub failures."""

        try:
            return self.github.get_repo(f"{owner}/{repo}")
        except BadCredentialsException as error:
            raise GitHubIntegrationError("The configured GitHub token is invalid.", 401) from error
        except RateLimitExceededException as error:
            raise GitHubIntegrationError("GitHub API rate limit exceeded.", 429) from error
        except GithubException as error:
            if error.status == 404:
                raise GitHubIntegrationError("Repository not found or not accessible with this token.", 404) from error
            if error.status == 409:
                raise GitHubIntegrationError("The repository is empty and has no branch to inspect.", 422) from error
            raise GitHubIntegrationError("GitHub API request failed.", 502) from error
        except Exception as error:
            raise GitHubIntegrationError("Unable to connect to GitHub.", 502) from error


def github_error(message: str, error: Exception) -> GitHubIntegrationError:
    """Translate a PyGithub error without exposing credentials or response bodies."""

    if isinstance(error, BadCredentialsException):
        return GitHubIntegrationError("The configured GitHub token is invalid.", 401)
    if isinstance(error, RateLimitExceededException):
        return GitHubIntegrationError("GitHub API rate limit exceeded.", 429)
    if isinstance(error, GithubException) and error.status == 404:
        return GitHubIntegrationError("The requested GitHub resource was not found.", 404)
    if isinstance(error, GithubException) and error.status == 409:
        return GitHubIntegrationError("The repository is empty and has no branch to inspect.", 422)
    return GitHubIntegrationError(message, 502)


def iso_datetime(value: Any) -> str | None:
    """Serialize GitHub datetime values consistently for normalized documents."""

    return value.isoformat() if value is not None else None


def user_name(user: Any) -> str | None:
    """Return a stable GitHub login when a user object is available."""

    return getattr(user, "login", None) if user is not None else None