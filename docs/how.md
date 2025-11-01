# How to Build and Use JobHunt

## Prerequisites
- Python 3.11+
- Git, Docker (optional)
- Chrome/Chromium installed (for Playwright)

## Setup
1. Clone the repo
   - git clone https://github.com/Anand0295/jobhunt
   - cd jobhunt
2. Create and activate a virtual environment
   - python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
3. Install dependencies
   - pip install -r requirements.txt
4. Install browsers for Playwright (if using)
   - playwright install
5. Configure environment
   - cp .env.example .env
   - Fill in API keys/tokens as needed

## Build/Run
- CLI usage
  - python -m jobhunt --help
  - jobhunt match --resume ./resumes/base.pdf --jobs ./inputs/jobs.csv
  - jobhunt apply --job-url <url> --profile ./profiles/user.yaml
- Docker (optional)
  - docker compose up --build

## Testing
- Run unit and integration tests
  - pytest
- Run E2E browser tests
  - pytest -k e2e --headed --browser chromium

## Updating Models/Providers
- Set provider via env (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)
- To use local models via Ollama, set OLLAMA_HOST and model name in config

## Troubleshooting
- Playwright timeouts
  - Ensure browsers installed; consider slowMo; check selectors
- Rate limits
  - Configure backoff and polite crawling settings
- ATS parsing issues
  - Provide clean PDF/JSON resume sources; adjust templates

## Contributing
- Fork and create a feature branch
- Run pre-commit and tests before PR
- Open a PR with a clear description and screenshots/logs if relevant

## License
- See LICENSE in the repository
