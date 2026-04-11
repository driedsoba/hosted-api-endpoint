# Fun Facts API

[![CI](https://github.com/driedsoba/hosted-api-endpoint/actions/workflows/ci.yml/badge.svg)](https://github.com/driedsoba/hosted-api-endpoint/actions/workflows/ci.yml)
[![Deploy](https://github.com/driedsoba/hosted-api-endpoint/actions/workflows/deploy.yml/badge.svg)](https://github.com/driedsoba/hosted-api-endpoint/actions/workflows/deploy.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![Terraform](https://img.shields.io/badge/terraform-IaC-purple)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A REST API serving fun facts with CRUD operations. Built with FastAPI, deployed to AWS Lambda + API Gateway via Terraform.

## Live API

**Base URL**: `https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev`

Swagger UI is available at `/docs` when running locally. The deployed API requires an API key on all routes, so Swagger UI is not accessible via the live URL — use the curl examples below instead.

> **Note**: The base URL may change on redeployment.

## Endpoints

| Method | Path | Description | Success | Error |
|--------|------|-------------|---------|-------|
| `GET` | `/api/v1/fun-facts/{id}` | Get a fun fact by ID | `200` with fact | `404` if not found |
| `POST` | `/api/v1/fun-facts` | Add a new fun fact | `201` with created fact | `409` duplicate title, `422` validation error |
| `DELETE` | `/api/v1/fun-facts/{id}` | Delete a fun fact | `204` no content | `404` if not found |
| Any | Any | Without `x-api-key` header | - | `403` forbidden |

### Authentication

All requests require an API key passed via the `x-api-key` header, enforced at the API Gateway level. The key will be provided separately.

### Try it out

**Get a fun fact** (seed data IDs are `fun-001` through `fun-007`):

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/fun-001
```

Response (`200`):

```json
{
  "id": "fun-001",
  "category": "tech",
  "title": "First Programming Language",
  "fact": "I wrote my first line of code in Python during university...",
  "fun_rating": 8,
  "added_at": "2026-04-10T08:00:00Z"
}
```

**Add a new fun fact**:

```bash
curl -X POST https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "tech",
    "title": "My First API",
    "fact": "I built this API as a take-home assignment",
    "fun_rating": 8
  }'
```

Response (`201`):

```json
{
  "id": "d6bab823-7aa6-4e16-85f4-45958ba03907",
  "category": "tech",
  "title": "My First Api",
  "fact": "I built this API as a take-home assignment",
  "fun_rating": 8,
  "added_at": "2026-04-11T07:22:04.871613Z"
}
```

**Delete a fun fact** (use the `id` from the POST response):

```bash
curl -X DELETE https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/{id} \
  -H "x-api-key: YOUR_API_KEY"
```

Response: `204 No Content`

**Error examples**:

```bash
# Missing API key --> 403
curl https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/fun-001

# Not found --> 404
curl -H "x-api-key: YOUR_API_KEY" \
  https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/nonexistent

# Duplicate title --> 409
# (POST the same title twice)

# Invalid payload --> 422
curl -X POST https://lhccxekb1b.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"category": "invalid", "title": "", "fact": "test", "fun_rating": 99}'
```

### Validation rules

- `category`: one of `hobbies`, `food`, `travel`, `music`, `sports`, `tech`, `random`
- `title`: 1-100 characters, whitespace stripped
- `fact`: 1-500 characters, whitespace stripped
- `fun_rating`: integer between 1 and 10

Duplicate titles (case-insensitive) return `409 Conflict`. Invalid payloads return `422 Unprocessable Entity`.

## Architecture

```text
                         ┌──────────────────────────────────────────────┐
                         │                  GitHub                      │
                         │                                              │
                         │  CI (on PR)         Deploy (on push to main) │
                         │  - Lint (ruff)      - Test                   │
                         │  - Test (pytest)    - Terraform Validate     │
                         │  - Security         - Checkov IaC Scan      │
                         │    (bandit)         - Plan                   │
                         │                     - Apply (manual approval)│
                         └──────────────┬───────────────────────────────┘
                                        │ OIDC
                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          AWS (ap-southeast-1)                             │
│                                                                           │
│  ┌─────────┐    ┌──────────────────────────────────┐    ┌──────────────┐ │
│  │         │    │        API Gateway (REST)         │    │  CloudWatch  │ │
│  │         │    │                                    │    │    Logs      │ │
│  │  IAM    │    │  - API Key auth (x-api-key)       │    │              │ │
│  │ (OIDC   │    │  - Usage Plan: 100 req/day        │    │  Log group:  │ │
│  │  Role)  │    │  - Throttle: 10/s, burst 20       │    │  /aws/lambda │ │
│  │         │    │  - Stage: dev                      │    │  /fun-facts- │ │
│  │         │    │  - Routes: ANY /{proxy+}, ANY /    │    │  api-dev     │ │
│  └─────────┘    └───────────────┬────────────────────┘    └──────────────┘ │
│                                 │                                ▲         │
│                                 ▼                                │ logs    │
│                  ┌──────────────────────────────────┐            │         │
│                  │      Lambda (Python 3.12)         │────────────┘         │
│                  │                                    │                     │
│                  │  lambda_handler.py                 │                     │
│                  │    └── Mangum (ASGI adapter)       │                     │
│                  │          └── FastAPI               │                     │
│                  │                │                   │                     │
│                  │    ┌───────────┼───────────┐       │                     │
│                  │    ▼           ▼           ▼       │                     │
│                  │  Middleware  Router     Dependencies│                     │
│                  │  (request   /api/v1/    (DI wiring) │                     │
│                  │   logger)   fun-facts       │       │                     │
│                  │               │        ┌────▼────┐  │                     │
│                  │               └───────►│ Service │  │                     │
│                  │                        │(business│  │                     │
│                  │                        │ logic)  │  │                     │
│                  │                        └────┬────┘  │                     │
│                  │                             ▼       │                     │
│                  │                        ┌─────────┐  │                     │
│                  │                        │  Repo   │  │                     │
│                  │                        │(in-mem  │  │                     │
│                  │                        │  dict)  │  │                     │
│                  │                        └────┬────┘  │                     │
│                  │                             ▼       │                     │
│                  │                        ┌─────────┐  │                     │
│                  │                        │  Seed   │  │                     │
│                  │                        │  Data   │  │                     │
│                  │                        │ (.json) │  │                     │
│                  │                        └─────────┘  │                     │
│                  └──────────────────────────────────────┘                     │
│                                                                           │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │      S3 (Terraform State)        │  │       CloudFormation         │   │
│  │                                  │  │                              │   │
│  │  Bucket: terraform-state-*       │  │  Stack: terraform-backend    │   │
│  │  Stores remote state file        │  │  Bootstraps the S3 bucket    │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

**Layered design**: Router --> Service --> Repository, wired via FastAPI's `Depends()` for dependency injection. The service layer enriches incoming data with server-generated fields (UUID, timestamp, title normalisation) before persisting to the repository.

### Request logging

All requests are logged via middleware with a unique request ID, HTTP method, path, status code, and duration. Log levels are determined by status code (2xx/3xx: INFO, 4xx: WARNING, 5xx: ERROR).

## Data

Fun facts are stored in `data/fun_facts.json` and loaded into memory on startup. No database is used -- this is by design per the assignment requirements. On Lambda, in-memory state resets when the instance recycles.

## Running Locally

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
uv sync
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### Run Tests

```bash
uv run pytest tests/ -v
```

### Lint and Security Scan

```bash
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
uv run bandit -r app/ -c pyproject.toml
```

## Project Structure

```text
app/
├── main.py              # FastAPI app entry point
├── models/              # Pydantic request/response schemas
├── routers/             # API route definitions
├── services/            # Business logic (dependency injection target)
├── repositories/        # In-memory data store
├── middleware/          # Request logging
└── dependencies.py      # DI wiring with Depends()
tests/
├── conftest.py          # Shared fixtures (mock repository, test client)
├── test_endpoints.py    # Integration tests (9 tests)
├── test_service.py      # Service unit tests (7 tests)
├── test_repository.py   # Repository unit tests (9 tests)
└── test_validation.py   # Pydantic validation tests (12 tests)
terraform/
├── main.tf              # Root module calling compute + network
└── modules/
    ├── compute/         # Lambda function + IAM
    └── network/         # API Gateway + API key + usage plan
```

## CI/CD

GitHub Actions pipeline:

- **CI** (on PR): lint --> test with coverage --> Bandit security scan
- **Deploy** (on push to main): test --> Terraform validate --> Checkov IaC scan --> plan --> apply (manual approval)
- **Destroy** (manual): tears down all infrastructure with environment approval
