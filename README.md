## Backend for Hearth

[![MIT License](https://img.shields.io/badge/license-MIT-9370d8.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/hearthweb/backend/actions/workflows/test.yml/badge.svg)](https://github.com/hearthweb/backend/actions/workflows/test.yml)

This repository contains the backend for Hearth. It communicates with the database, handles authentication, serialization, job management, etc.

### Running the Application

The officially supported way of running the backend is via Docker container:

```
docker run \
    --name backend \
    -P \
    --env SECRET_KEY=Password1234 \
    ghcr.io/hearthweb/backend:latest
```
