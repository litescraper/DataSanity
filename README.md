# DataSanity

DataSanity is an AI-powered web application for dataset cleaning, synthetic data generation, vectorization, and data enrichment using natural language prompts.

## Features

- Dataset cleaning with LLM detection of noisy, missing, or duplicate values
- Synthetic data generation based on schema or prompt
- Vectorization for RAG pipelines
- Data enrichment using web search APIs
- Natural language prompt-based workflow
- Support for CSV uploads and downloads

## Tech Stack

- Frontend: Next.js with Tailwind CSS
- Backend: FastAPI (Python)
- LLM Inference: OpenRouter API
- Data Processing: pandas, numpy
- Embedding: sentence-transformers
- Vector Store: FAISS
- Web Search: Exa or Serper.dev
- Storage: SQLite + local filesystem

## Optional web context for enrichment

Unset or empty base URL overrides keep the provider default. Custom path
prefixes and trailing slashes are supported.

Support any Serper.dev-compatible endpoint (like litescrape.com, serpbase.dev, serpensapi.org, and others)

Set `SEARCH_PROVIDER=serper` and `SERPER_API_KEY` for Serper-compatible search
in the enrichment route. `SERPER_BASE_URL` defaults to
`https://google.serper.dev`; requests append `/search` and use `X-API-KEY`
authentication.

The API-backed mode submits only the enrichment prompt, not dataset rows,
and returns real titles, source URLs and snippets. These results are web context,
not proof that individual dataset values have been validated or enriched. It
does not call OpenRouter. Leaving `SEARCH_PROVIDER` unset retains the existing
MVP demonstration behavior, including its simulated example entries.
