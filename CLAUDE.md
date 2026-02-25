# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python web scraping project using `requests` and `BeautifulSoup4`. The project name suggests it is intended to scrape Korean bus terminal data, though the current implementation targets NAVER Knowledge-IN (지식IN).

## Setup & Commands

```bash
# Install dependencies
poetry install

# Run the main script
python terminal_info.py

# Or via poetry
poetry run python terminal_info.py
```

Python 3.13+ is required. The `.venv` virtual environment is already present.

## Architecture

This is a single-file script project:

- [terminal_info.py](terminal_info.py) — Entry point. Makes an HTTP GET request, parses the HTML response with BeautifulSoup, and prints the result.
- [pyproject.toml](pyproject.toml) — Poetry project config with dependencies (`beautifulsoup4`, `requests`).

There is no package structure, test suite, or linting configuration.