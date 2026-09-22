from ai.preprocess import prepare_documents
from backend.models.github_models import (
    NormalizedDocument,
    RepositoryContext,
)

repository = NormalizedDocument(
    repository="demo/project",
    type="repository",
    id="repo-1",
    title="Demo Project",
    content="A sample authentication project.",
)

issue = NormalizedDocument(
    repository="demo/project",
    type="issue",
    id="247",
    title="Authentication timeout",
    content="Users are getting logged out after 10 minutes.",
    author="developer1",
    timestamp="2026-09-10",
    metadata={"number": 247},
)

commit = NormalizedDocument(
    repository="demo/project",
    type="commit",
    id="a83f21",
    title="Update JWT expiry",
    content="Changed JWT expiration from 30 minutes to 10 minutes.",
    author="developer2",
    timestamp="2026-09-11",
    metadata={"sha": "a83f21"},
)

context = RepositoryContext(
    repository=repository,
    issues=[issue],
    commits=[commit],
)

documents = prepare_documents(context)

print("Documents:", len(documents))

for document in documents:
    print("\n----------------")
    print(document["text"])
    print(document["metadata"])