#!/usr/bin/env bash
# Base Dev Image Setup and Tests
set -e  # Exit on error

# Install dependencies
uv sync

# Run tests
uv run nox -s test

# Format and lint
uv run nox -s fmt
uv run nox -s lint -- --pyright --ruff

# config git for container
git config --global --add safe.directory /workspace
