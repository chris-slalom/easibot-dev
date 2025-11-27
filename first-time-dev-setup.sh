# Base Dev Image Setup and Tests
# Install dependencies
uv sync

# Run tests
uv run nox -s test

# Format and lint
uv run nox -s fmt
uv run nox -s lint -- --pyright --ruff
