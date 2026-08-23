## Backend for Hearth

[![MIT License](https://img.shields.io/badge/license-MIT-9370d8.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/hearthweb/backend/actions/workflows/test.yml/badge.svg)](https://github.com/hearthweb/backend/actions/workflows/test.yml)

This repository contains the backend for Hearth. It communicates with the database, handles authentication, serialization, job management, etc.

If you are looking to run Hearth in production, please consult the [app](https://github.com/hearthweb/app) repository.

### Local Development

The backend uses the [uv](https://docs.astral.sh/uv/) package manager. Once installed, setting up application dependencies is as simple as:

```
uv sync
```

Starting the application in dev mode can be done with:

```
uv run fastapi dev
```

This will use a local SQLite database and `./upload` for storage.

### Testing

To run the test suite for the backend, use the following command:

```
uv run pytest
```
