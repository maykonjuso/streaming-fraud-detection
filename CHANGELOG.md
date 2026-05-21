# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-21

### Bug Fixes

- Loosen pydantic pin to satisfy mcp>=1.0.0 requirement (>=2.8.0)
- Resolve starlette conflict — loosen fastapi/mcp/api pins to >=bounds
- Add __init__.py files, pythonpath config and requirements-test.txt for CI
- Sort imports in api/main.py (ruff I001)
- Suppress third-party warnings in pytest (opentelemetry DeprecationWarning, pyod RuntimeWarning)
- **ci:** Replace docker-based git-cliff action with direct binary install
- **ci:** Correct git-cliff binary filename (no v prefix)

### Chores

- Fix all ruff lint errors (F401, I001, UP017, UP042, UP045, F841)
- Add missing project files for production-grade completeness

### Features

- Initial project scaffold

### Style

- Apply ruff format to 13 files


