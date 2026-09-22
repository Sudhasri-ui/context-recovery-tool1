from ai.preprocess import prepare_documents
from ai.embeddings import create_embeddings
from ai.retrieval import retrieve_documents

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
)

commit = NormalizedDocument(
    repository="demo/project",
    type="commit",
    id="a83f21",
    title="Update JWT expiry",
    content="Changed JWT expiration from 30 minutes to 10 minutes.",
)

context = RepositoryContext(
    repository=repository,
    issues=[issue],
    commits=[commit],
)

documents = prepare_documents(context)

embeddings = create_embeddings(documents)

task = "Fix the authentication timeout problem"

results = retrieve_documents(
    task,
    documents,
    embeddings,
    top_k=3,
)

print("Task:", task)

for result in results:
    print("\n----------------")
    print("Score:", result["score"])
    print("Type:", result["metadata"]["type"])
    print("Title:", result["metadata"]["title"])
    print("Content:", result["metadata"].get("metadata"))