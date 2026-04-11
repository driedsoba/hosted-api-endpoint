# Fun Facts API

A REST API serving fun facts with CRUD operations. Built with FastAPI, deployed to AWS Lambda + API Gateway via Terraform.

## Live API

**Base URL**: `https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev`

Interactive API docs (Swagger UI): [https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev/docs](https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev/docs)

> **Note**: The URLs above are environment-specific and may change on redeployment. The current base URL can be retrieved via `terraform output api_gateway_url`.

## Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `GET` | `/api/v1/fun-facts/{id}` | Get a fun fact by ID | 200, 404 |
| `POST` | `/api/v1/fun-facts` | Add a new fun fact | 201, 409, 422 |
| `DELETE` | `/api/v1/fun-facts/{id}` | Delete a fun fact | 204, 404 |

### Authentication

All requests require an API key passed via the `x-api-key` header. The key will be provided separately.

### Try it out

**Get a fun fact** (seed data IDs are `fun-001` through `fun-007`):

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/fun-001
```

**Add a new fun fact**:

```bash
curl -X POST https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "tech",
    "title": "My First API",
    "fact": "I built this API as a take-home assignment",
    "fun_rating": 8
  }'
```

**Delete a fun fact** (use the `id` from the POST response):

```bash
curl -X DELETE https://4hlz4ky7y0.execute-api.ap-southeast-1.amazonaws.com/dev/api/v1/fun-facts/{id} \
  -H "x-api-key: YOUR_API_KEY"
```

### Validation rules

- `category`: one of `hobbies`, `food`, `travel`, `music`, `sports`, `tech`, `random`
- `title`: 1-100 characters, whitespace stripped
- `fact`: 1-500 characters, whitespace stripped
- `fun_rating`: integer between 1 and 10

Duplicate titles (case-insensitive) return `409 Conflict`. Invalid payloads return `422 Unprocessable Entity`.

## Architecture

```text
Client → API Gateway → Lambda → FastAPI
                                  ├── Router (/api/v1/fun-facts)
                                  ├── Service (business logic, DI)
                                  └── Repository (in-memory store)
```

**Layered design**: Router → Service → Repository, wired via FastAPI's `Depends()` for dependency injection. The service layer processes incoming data (UUID generation, timestamp, title normalisation) before persisting to the repository.

## Data

Fun facts are stored in `data/fun_facts.json` and loaded into memory on startup. No database is used - this is by design per the assignment requirements. On Lambda, in-memory state resets when the instance recycles.

## Running Tests

```bash
uv sync
uv run pytest tests/ -v
```

## Project Structure

```text
app/
├── main.py              # FastAPI app entry point
├── models/              # Pydantic request/response schemas
├── routers/             # API route definitions
├── services/            # Business logic (dependency injection target)
├── repositories/        # In-memory data store
├── middleware/           # Request logging
└── dependencies.py      # DI wiring with Depends()
terraform/
├── main.tf              # Root module calling compute + network
└── modules/
    ├── compute/         # Lambda function + IAM
    └── network/         # API Gateway
```

## CI/CD

GitHub Actions pipeline: test → validate → security scan (Checkov) → plan → apply (manual approval).
