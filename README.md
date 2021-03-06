# FX Service

[![CircleCI](https://circleci.com/gh/sam-atkins/fx_service/tree/main.svg?style=svg)](https://circleci.com/gh/sam-atkins/fx_service/tree/main)
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Description

Foreign Exchange API service.

## Development

Prerequisites:

* Python 3
* Docker Desktop
* [Serverless](https://serverless.com/)

### Build and run locally

```bash
docker-compose up --build
```

### Tests

```bash
# Run the container and get to the bash line
docker-compose run --entrypoint="" fx_service-test /bin/bash

# run tests
pytest -vv

# run tests, with --cov flag to run coverage report
pytest -vv --cov
```

## Deploy

```bash
sls deploy
```
