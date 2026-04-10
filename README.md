# Fun Facts API

A REST API serving fun facts with CRUD operations. Built with FastAPI, deployed to AWS Lambda + API Gateway via Terraform.

## Architecture

```text
Client → API Gateway → Lambda → FastAPI
                                  ├── Router (/api/v1/fun-facts)
                                  ├── Service (business logic, DI)
                                  └── Repository (in-memory store)
```

**Layered design**: Router → Service → Repository, wired via FastAPI's `Depends()` for dependency injection. The service layer processes incoming data (UUID generation, timestamp, title normalisation) before persisting to the repository.

## Endpoints

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| `GET` | `/api/v1/fun-facts/{id}` | Get a fun fact by ID | 200, 404 |
| `POST` | `/api/v1/fun-facts` | Add a new fun fact | 201, 409, 422 |
| `DELETE` | `/api/v1/fun-facts/{id}` | Delete a fun fact | 204, 404 |

### Request body (POST)

```json
{
  "category": "tech",
  "title": "My First API",
  "fact": "I built this API as a take-home assignment",
  "fun_rating": 8
}
```

**Validation rules**:
- `category`: one of `hobbies`, `food`, `travel`, `music`, `sports`, `tech`, `random`
- `title`: 1-100 characters, whitespace stripped
- `fact`: 1-500 characters, whitespace stripped
- `fun_rating`: integer between 1 and 10

## Local Development

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
uv sync
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

### Run Tests

```bash
uv run pytest tests/ -v --cov=app
```

### Lint

```bash
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/
```

## Data

Fun facts are stored in `data/fun_facts.json` and loaded into memory on startup. No database is used - this is by design per the assignment requirements. On Lambda, in-memory state resets when the instance recycles.

## Deployment

### 1. Bootstrap Terraform State

Deploy the CloudFormation stack to create the S3 bucket for Terraform remote state:

```bash
aws cloudformation deploy \
  --template-file bootstrap/cfn-terraform-backend.yaml \
  --stack-name terraform-backend
```

### 2. Deploy Infrastructure

```bash
# Package Lambda dependencies
mkdir -p package
uv export --no-dev --no-hashes > requirements.txt
uv pip install --target package -r requirements.txt
cp -r app lambda_handler.py data package/

# Deploy with Terraform
cd terraform
terraform init
terraform plan
terraform apply
```

The API Gateway URL will be output after `terraform apply`.

### CI/CD

The GitHub Actions pipeline handles deployment automatically:

- **CI** (on PR): lint → test with coverage
- **Deploy** (on push to main): test → validate → security scan (checkov) → plan → apply

AWS credentials are configured via OIDC role assumption (`AWS_ROLE_ARN` secret).

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
