# Context Recovery

Context Recovery reconstructs the history behind a GitHub codebase. It collects repository metadata, issues, pull requests, reviews, comments, commits, and source files, then uses retrieval and AI reasoning to produce an evidence-backed context card for a developer task.

## Features

- FastAPI backend with normalized GitHub documents.
- Semantic document preparation, embeddings, and retrieval.
- Gemini-powered reasoning over retrieved GitHub evidence.
- Browser workspace served by the API at `/`.
- Demo fallback in the frontend when the API or a live repository is unavailable.

## Requirements

- Python 3.10 or newer
- A GitHub personal access token with access to the repositories you want to inspect
- A Gemini API key for the `/recover` endpoint

## Setup

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your credentials:

```text
GITHUB_TOKEN=your_github_token
GEMINI_API_KEY=your_gemini_api_key
```

Credentials are loaded with `python-dotenv` and should not be committed. The repository's `.gitignore` excludes `.env` files.

## Run

Start the development server from the project root:

```bash
python -m uvicorn backend.main:app --reload
```

Open these URLs in a browser:

- `http://127.0.0.1:8000/` for the Context Recovery workspace
- `http://127.0.0.1:8000/docs` for interactive API documentation
- `http://127.0.0.1:8000/health` for a health check

## Deploy To Vercel

This repository is configured to deploy the frontend and FastAPI backend as one Vercel project.

1. Import the GitHub repository into Vercel. A collaborator can do this if the repository is visible through the Vercel GitHub integration.
2. Keep the project root as the repository root. Do not set `frontend` as the root directory.
3. Add these environment variables in the Vercel project settings:

	```text
	GITHUB_TOKEN=your_github_token
	GEMINI_API_KEY=your_gemini_api_key
	```

4. Deploy. Vercel uses `api/index.py` as the Python entrypoint and `vercel.json` routes requests to the FastAPI application.
5. Open the generated deployment URL and check `/health` before trying a live repository recovery.

The Vercel deployment uses scikit-learn TF-IDF retrieval so it does not need to download a transformer model during serverless startup.

## API

Replace `OWNER` and `REPO` with a repository you can access:

```text
GET  /repository/OWNER/REPO
GET  /repository/OWNER/REPO/issues
GET  /repository/OWNER/REPO/issues/42/comments
GET  /repository/OWNER/REPO/pulls
GET  /repository/OWNER/REPO/pulls/42/comments
GET  /repository/OWNER/REPO/pulls/42/reviews
GET  /repository/OWNER/REPO/pulls/42/commits
GET  /repository/OWNER/REPO/pulls/42/files
GET  /repository/OWNER/REPO/commits
GET  /repository/OWNER/REPO/files
GET  /repository/OWNER/REPO/context
POST /repository/OWNER/REPO/recover
```

The recovery endpoint accepts a task and optional result count:

```bash
curl -X POST http://127.0.0.1:8000/repository/OWNER/REPO/recover \
	-H 'Content-Type: application/json' \
	-d '{"task":"Investigate the authentication timeout", "top_k":5}'
```

The `/context` endpoint returns normalized GitHub records grouped into `repository`, `issues`, `pull_requests`, `commits`, `files`, and `comments_reviews`. The `/recover` endpoint runs the full pipeline: collect context, prepare documents, create embeddings, retrieve relevant evidence, generate reasoning, and build a context card.

## Tests

Run the test suite from the project root:

```bash
pytest
```

The unit tests cover preprocessing, embeddings, retrieval, reasoning, and context-card construction using local sample data.
