## Backend for Hearth

[![MIT License](https://img.shields.io/badge/license-MIT-9370d8.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/hearthweb/backend/actions/workflows/test.yml/badge.svg)](https://github.com/hearthweb/backend/actions/workflows/test.yml)

This repository contains the backend for Hearth. It is written in Python and uses [FastAPI](https://fastapi.tiangolo.com) and [SQLModel](https://sqlmodel.tiangolo.com). It communicates with the database, handles authentication, serialization, and job management.

If you are looking to run Hearth in production, please consult the [app](https://github.com/hearthweb/app) repository.

### Local Development

The backend uses the [uv](https://docs.astral.sh/uv/) package manager. Once installed, setting up application dependencies is as simple as:

```
uv sync
```

By default, the application uses a local SQLite database and `./upload` for storage when running in dev mode. The database will need to be initialized and the first user created with:

```
uv run cli init-db
uv run cli create-user
```

The application can then be started with:

```
uv run fastapi dev
```

To browse the OpenAPI docs, visit http://localhost:8000/docs.

### Testing

To run the test suite for the backend, use the following command:

```
uv run pytest
```
