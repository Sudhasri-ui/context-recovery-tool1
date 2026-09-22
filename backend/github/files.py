"""Text source-file retrieval from a repository tree."""

from __future__ import annotations

import base64
from pathlib import PurePosixPath

from backend.github.client import GitHubClient, github_error
from backend.models.github_models import NormalizedDocument


SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css", ".md", ".json", ".yaml", ".yml"}
MAX_FILE_BYTES = 1_000_000


def get_repository_files(client: GitHubClient, owner: str, repo: str) -> list[NormalizedDocument]:
    """Retrieve supported, reasonably sized text files from the default branch."""

    repository = client.get_repository(owner, repo)
    try:
        repository_name = f"{owner}/{repo}"
        branch = repository.default_branch
        tree = repository.get_git_tree(branch, recursive=True)
        documents = []
        for tree_item in tree.tree:
            path = PurePosixPath(tree_item.path)
            if tree_item.type != "blob" or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if tree_item.size is not None and tree_item.size > MAX_FILE_BYTES:
                continue
            try:
                content_file = repository.get_contents(tree_item.path, ref=branch)
                raw_content = base64.b64decode(content_file.content).decode("utf-8")
            except (UnicodeDecodeError, ValueError):
                continue
            except Exception as error:
                raise github_error(f"Unable to retrieve repository file: {tree_item.path}.", error) from error
            documents.append(
                NormalizedDocument(
                    repository=repository_name,
                    type="file",
                    id=f"file-{tree_item.sha}",
                    title=path.name,
                    content=raw_content,
                    url=content_file.html_url,
                    metadata={
                        "path": tree_item.path,
                        "file_name": path.name,
                        "file_type": path.suffix.lower(),
                        "branch": branch,
                        "size": tree_item.size,
                        "sha": tree_item.sha,
                    },
                )
            )
        return documents
    except Exception as error:
        if hasattr(error, "status_code"):
            raise
        raise github_error("Unable to retrieve repository files.", error) from error