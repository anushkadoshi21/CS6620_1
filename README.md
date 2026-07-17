# CS6620_1

CI/CD & Workflow assignment.

## What this project is

A small FastAPI application that exposes a CRUD API for managing clients. It persists data to real AWS-style services — a **DynamoDB** table (source of truth) plus an **S3** bucket (a JSON copy of each client) — both emulated locally by **LocalStack**. There is no in-memory dictionary anymore; every request talks to DynamoDB/S3 through the AWS SDK (`boto3`).

Both the DynamoDB table and the S3 bucket are named `clients` and are created automatically when the LocalStack container starts (init script: [localstack/init/create-resources.sh](localstack/init/create-resources.sh)).

Writes are kept consistent across the two stores: `create`/`update`/`delete` write to DynamoDB first, then S3, and roll back the DynamoDB change if the S3 step fails.

A client has these fields:

- `name` — the primary key (DynamoDB hash key and S3 object key)
- `organization_type`
- `total_headcount`
- `total_valuation`
- `billed_amount`
- `amount_paid`

`total_headcount`, `total_valuation`, `billed_amount`, and `amount_paid` are all non-negative (`ge=0`).

## Project layout

```
app/
├── main.py                     # FastAPI app
├── models/
│   ├── client.py               # Pydantic models (ClientCreate/Update/Response)
│   └── health.py
├── routes/
│   ├── client.py               # /clients endpoints
│   └── health.py               # /health endpoint
└── services/
    ├── client_service.py       # CRUD logic against DynamoDB + S3 (via boto3)
    └── health_service.py

localstack/
└── init/
    └── create-resources.sh     # creates the DynamoDB table + S3 bucket on startup

compose.apiStack.yml            # localstack + api (dev stack)
compose.apiTest.yml             # localstack + api + tests (CI stack)
Dockerfile.api                  # image for the API
Dockerfile.tests                # image that runs pytest

scripts/
├── run_api.sh                  # build & run the API image only
├── run_apiStack.sh             # bring up localstack + api via compose
├── run_apiTestsStack.sh        # bring up the full test stack (used by CI)
└── run_tests.sh               # build & run the test image only

tests/
├── conftest.py                 # httpx/boto3 clients + state fixtures
└── test_client_routes.py       # endpoint tests (the suite compose runs)
```

## API endpoints

Clients are addressed by their **`name`** (the primary key), not a UUID.

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Create a new client (409 if the name already exists) |
| GET | `/clients/{name}` | Get one client by name |
| PUT | `/clients/{name}` | Update a client |
| DELETE | `/clients/{name}` | Delete a client |

`{name}` must be at least 2 characters and match `^[a-zA-Z-]+$`; anything else returns `422`.

Interactive docs are auto-generated at `/docs` (Swagger UI) and `/redoc` once the app is running.

## Setup

You need **Docker** (with Compose) to run LocalStack. For local Python work you also need Python 3.12+.

```bash
# create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

Because the app now talks to DynamoDB and S3, it needs those services available. The easiest way to run everything (LocalStack + the API) is the compose stack described below.

## How to run the application

### Option A — full stack with Docker Compose (recommended)

```bash
bash scripts/run_apiStack.sh
```

This brings up two containers from [compose.apiStack.yml](compose.apiStack.yml): **LocalStack** (DynamoDB + S3 on port `4566`) and the **API** (port `8000`). LocalStack seeds the `clients` table and bucket on startup, and the API waits until LocalStack reports healthy before it starts. Open `http://localhost:8000/docs` to try the endpoints.

### Option B — API from source (LocalStack still required)

Start LocalStack (e.g. via the compose stack above, or your own LocalStack), then point the app at it and run:

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

uvicorn app.main:app --reload
```

The service reads `AWS_ENDPOINT_URL` (default `http://localhost:4566`) and `AWS_REGION` (default `us-east-1`) from the environment, so with LocalStack running on the defaults it works out of the box. The `--reload` flag restarts the server when you edit code — drop it in production.

## About the tests

The test stack (`compose.apiTest.yml` / `Dockerfile.tests`) runs a single suite — **`tests/test_client_routes.py`** — against a **live API** talking to **real DynamoDB and S3** (LocalStack). Everything it needs is provided by **`tests/conftest.py`**.

### `conftest.py` — fixtures

- **`api`** — session-scoped `httpx.Client` pointed at `API_URL` (default `http://localhost:8000`); used to hit the API over HTTP.
- **`dynamo`** / **`s3`** — session-scoped `boto3` clients pointed at `AWS_ENDPOINT_URL` (default `http://localhost:4566`), used to inspect the two stores directly.
- **`sample_client`** — a valid client payload for create/update tests.
- **`clean_state`** — wipes both DynamoDB and S3 before and after the test, so it starts from an empty state.
- **`seeded_client`** — wipes both stores, POSTs `sample_client`, and yields that payload (then cleans up), for tests that need one existing client.

These keep every test isolated and order-independent by fully wiping DynamoDB **and** S3 around each test.

### `test_client_routes.py` — endpoint tests

Drives each endpoint over HTTP and, crucially, asserts the **two stores stay consistent** — helpers `_assert_s3_dynamo_match` (DynamoDB item equals the S3 JSON copy) and `_assert_neither_s3_dynamo_has` (name absent from both). Coverage:

- **List** — empty list, and listing after a client is seeded.
- **Get** — found, `404` for a missing name, `422` for an invalid name (e.g. digits).
- **Create** — `201` on success, `409` on duplicate name, `422` for a missing required field or negative headcount.
- **Update** — `200` on a `PUT` that changes a field, `404` for a missing client.
- **Delete** — `204` on success, `404` for a missing client.

## How to run tests manually

The suite needs a running API and LocalStack. The simplest path is the compose stack (`bash scripts/run_apiTestsStack.sh`). To instead run `pytest` from your venv, start LocalStack + the API first (e.g. `bash scripts/run_apiStack.sh`), then point the tests at them and run pytest from the project root:

```bash
export API_URL=http://localhost:8000
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# the suite compose runs
pytest tests/test_client_routes.py -v

# a single class
pytest tests/test_client_routes.py::TestCreateClient -v

# a single test
pytest tests/test_client_routes.py::TestCreateClient::test_creates -v
```

## Run with Docker

The app and its tests are packaged into images (`Dockerfile.api`, `Dockerfile.tests`) and wired together with LocalStack via Docker Compose. Convenience scripts live in `scripts/` and `cd` to the repo root themselves, so you can run them from anywhere.

Because the API depends on DynamoDB and S3, the **compose stacks** (see [How to run the application](#how-to-run-the-application) and [Run the tests](#run-the-tests) above) are the way to get a working API or test run. The single-image scripts below are lower-level building blocks.

### Run the API image only

```bash
bash scripts/run_api.sh
```

This builds the `Dockerfile.api` image and runs it in the foreground, publishing port `8000`. Note this runs the API **alone** — with no LocalStack reachable, requests to `/clients` will fail; use `scripts/run_apiStack.sh` for a working API. Stop it with `Ctrl-C`.

Equivalent manual commands:

```bash
docker build -f Dockerfile.api -t myapp-api:latest .
docker run --rm -p 8000:8000 myapp-api:latest
```

### Run the tests

Because the tests exercise the API against real DynamoDB/S3, they run against the full stack (LocalStack + API + a test container) defined in [compose.apiTest.yml](compose.apiTest.yml):

```bash
bash scripts/run_apiTestsStack.sh
```

This brings up LocalStack, waits for it (and the API) to be healthy, then runs the `tests` container (`pytest`). Compose is invoked with `--exit-code-from tests --abort-on-container-exit`, so the whole stack tears down when the tests finish and the script **exits with the test container's exit code** — 0 if all tests pass, non-zero if any fail. This is exactly the pass/fail signal the CI gate relies on.

Equivalent manual command:

```bash
docker compose -f compose.apiTest.yml up --build --exit-code-from tests --abort-on-container-exit
```

> The older `scripts/run_tests.sh` / `Dockerfile.tests` image can still be built on its own, but the suite needs LocalStack and the API reachable, so the compose stack above is the supported way to run it.

## How tests run in CI (GitHub Actions)

CI is defined in [.github/workflows/ci.yml](.github/workflows/ci.yml). It runs on every **push to `main`**, every **pull request targeting `main`**, and can also be **triggered manually** from the Actions tab (`workflow_dispatch`). On each run, GitHub Actions:

1. Checks out the code.
2. Runs `bash ./scripts/run_apiTestsStack.sh`, which spins up the full Docker Compose stack (LocalStack + API + tests) and runs the suite against it. The step fails if any test fails — compose is run with `--exit-code-from tests`, so the test container's non-zero exit propagates out of the script and fails the job.
3. Posts a status summary to Slack — this step runs **always** (on both success and failure) and reports the real outcome (`success` / `failure`), the branch, the commit, and a link to the run.

You can see the run in the **Actions** tab of the GitHub repo. A green check on a PR means the suite passed; a red X blocks the PR.

### Slack notifications

The notify step uses an [incoming webhook](https://api.slack.com/messaging/webhooks). 
If the secret is absent the workflow still runs the tests; only the Slack step fails to deliver.

Please not that content of code (boilerplate and small portion of logic) and documentation has been generated using Claude code AI.
