# Tools & Technologies

This document explains the selected tools and technologies used in JobHunt, with rationale and references.

## Core Languages & Runtime
- Python 3.11+
  - Reason: rich ecosystem for data/AI, mature HTTP/automation libs, type hints
  - Evidence: Widely adopted for AI/ML and automation (PyPI, HuggingFace, OpenAI, Selenium)
- Node.js (optional services / adapters)
  - Reason: fast I/O for webhooks/integrations; ecosystem for scraping/proxying

## AI & NLP Stack
- LLM provider abstraction (OpenAI / Anthropic / local via Ollama)
  - Reason: pluggable models; cost/performance flexibility; privacy-preserving local option
- Embeddings (text-embedding-3-large or equivalent)
  - Reason: semantic search for resume/job matching and memory
- Prompt tooling (Guidance/LangChain/LlamaIndex)
  - Reason: composable agents, chains, retrieval augmentation

## Automation & Scraping
- Playwright (primary) and Selenium (fallback)
  - Reason: reliable browser automation; anti-bot resilience; multi-browser support
  - Evidence: Playwright CI reliability, official MS maintenance, robust wait APIs
- Requests/HTTPX + BeautifulSoup/Selectolax
  - Reason: lightweight scraping/crawling where full browser isn’t needed

## Data & Storage
- SQLite + SQLModel/SQLAlchemy
  - Reason: zero-ops local DB for jobs, applications, artifacts; easy to swap to Postgres
- File storage: local filesystem + optional S3 compatible (MinIO)
  - Reason: store resumes, tailored variants, logs, exports
- Vector store: FAISS or Chroma
  - Reason: fast local semantic search without managed services

## Orchestration & Workflow
- Pydantic v2 for typed configs and validation
- Prefect (or Temporal) for workflows and retries
  - Reason: observable, resilient job runs; scheduling; distributed workers when needed
- Celery/RQ (optional) for background jobs

## CLI & Apps
- Typer (CLI) + Rich (UX)
  - Reason: friendly CLI with autocompletion and nice output
- FastAPI (optional) for API/UI backend
  - Reason: share Python models, async I/O, OpenAPI, easy auth

## Quality & Testing
- pytest + pytest-playwright
  - Reason: end-to-end automation tests; fixtures for browsers
- ruff + mypy
  - Reason: fast linting and static typing for maintainability
- pre-commit
  - Reason: consistent formatting (black/ruff), secrets scans

## DevOps
- GitHub Actions
  - Reason: CI for tests, lint, packaging, release
- Docker + docker-compose
  - Reason: reproducible dev; easy onboarding; parity between local and prod

## Security & Compliance
- python-dotenv + secret scanning (Gitleaks)
  - Reason: config hygiene; prevent secret leaks
- Rate-limiting, polite crawling, ToS-aware automation policies

## References & Proof
- Playwright: https://playwright.dev/docs/intro
- FastAPI: https://fastapi.tiangolo.com
- SQLModel: https://sqlmodel.tiangolo.com/
- Prefect: https://docs.prefect.io/
- FAISS: https://faiss.ai/
- Chroma: https://docs.trychroma.com/
- LangChain: https://python.langchain.com
- LlamaIndex: https://docs.llamaindex.ai

These choices prioritize reliability, transparency, and local-first operation while allowing cloud upgrades if needed.
