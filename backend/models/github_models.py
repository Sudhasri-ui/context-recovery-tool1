"""Common normalized models shared by all GitHub data sources."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


DocumentType = Literal["repository", "issue", "comment", "pull_request", "review", "commit", "file"]


class NormalizedDocument(BaseModel):
    """A retrieval-ready record independent of the GitHub API object shape."""

    source: Literal["github"] = "github"
    repository: str
    type: DocumentType
    id: str
    title: str | None = None
    content: str = ""
    author: str | None = None
    timestamp: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    url: str | None = None


class RepositoryContext(BaseModel):
    """Complete normalized context collected for one repository."""

    repository: NormalizedDocument
    issues: list[NormalizedDocument] = Field(default_factory=list)
    pull_requests: list[NormalizedDocument] = Field(default_factory=list)
    commits: list[NormalizedDocument] = Field(default_factory=list)
    files: list[NormalizedDocument] = Field(default_factory=list)
    comments_reviews: list[NormalizedDocument] = Field(default_factory=list)