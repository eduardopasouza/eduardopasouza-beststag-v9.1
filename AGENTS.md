# Agent Instructions for BestStag v9.1 Repository

This file is located at the root of the repository (`/AGENTS.md`). It defines how automated agents (like Codex) should interact with the code base.

## Coding Guidelines

- **Language Style**: Use `Black` and `isort` for Python code (line length 100). For TypeScript code use `Prettier`.
- **Linting**: Run `make lint` before committing.
- **Formatting**: Run `make format` to format Python and TypeScript code.
- **Tests**: Run `make test` for unit tests or `make test-all` for the full suite. Ensure the minimum coverage remains above 80%.
- **Commits**: Follow the Conventional Commits specification.

## Development Workflow

1. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   pip install -r config/requirements_fase2.txt
   pip install -r tests/requirements.txt
   npm install
   cd src/frontend && npm install
   ```
2. Run `make dev` to start the development environment (Docker based).
3. To run just the backend in development mode:
   ```bash
   uvicorn src.backend.app:app --reload --port 8000
   ```
4. For frontend development:
   ```bash
   cd src/frontend && npm start
   ```

## Testing

- The test suite lives under `tests/`. See `tests/README.md` for detailed instructions.
- Use `make test` for a quick run, or `make test-all` for the entire automation suite.
- When adding new code, ensure the tests pass and coverage targets are met.

## Pull Requests

- Keep PRs focused. Update documentation when behavior changes.
- After committing, ensure `git status` shows a clean working tree.
- The pull request summary should mention key code or documentation changes.

