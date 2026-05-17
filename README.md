# CS6620_1

CI/CD & Workflow assignment.

## What this project is

A small FastAPI application that exposes a CRUD API for managing clients. It does not use a real database here and instead, it keeps clients in memory and seeds them from a constants.py file on startup. 

A client has these fields:

- `name`
- `organization_type`
- `total_headcount`
- `joined_at`
- `total_valuation`
- `billed_amount`
- `amount_paid`
- `latest_transaction_date` (optional)

## Project layout

```
app/
├── main.py                     # FastAPI app
├── constants.py                # In-memory seed data
├── models/
│   ├── client.py               # Pydantic models:
│   └── health.py
├── routes/
│   ├── client.py               # /clients endpoints
│   └── health.py               # /health endpoint
└── services/
    ├── client_service.py       # CRUD logic against the in-memory store
    └── health_service.py

tests/
├── conftest.py                 # TestClient, autouse reseed
├── test_models.py              # Pydantic model validation
├── test_client_service.py      # Service-layer unit tests
├── test_client_routes.py       # Endpoint tests
├── test_client_flow.py         # Scenario tests
└── test_health.py
```

## API endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Create a new client |
| GET | `/clients/{id}` | Get one client by id |
| PATCH | `/clients/{id}` | Partially update a client |
| DELETE | `/clients/{id}` | Delete a client |

Interactive docs are auto-generated at `/docs` (Swagger UI) and `/redoc` once the app is running.

## Setup

You need Python 3.12+.

```bash
# create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## How to run the application

From the project root:

```bash
uvicorn app.main:app --reload
```

This starts the app at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` in a browser to try the endpoints interactively. The `--reload` flag restarts the server when you edit code — drop it in production.

## About the tests

There are two flavors of tests in this repo:

### 1. Unit tests (isolated)

Each test resets the in-memory store back to `DUMMY_CLIENTS` before it runs (an autouse fixture in `conftest.py` handles this). That means every test starts from the same known state and can run in any order.

- **`test_models.py`** — Pydantic validation: required fields, non-negative constraints, optional fields, auto-generated UUIDs.
- **`test_client_service.py`** — service-layer CRUD: list / get / create / update / delete, including "not found" returns.
- **`test_client_routes.py`** — endpoint behavior: status codes (200, 201, 204, 404, 422), partial PATCH preserving unchanged fields, invalid UUID handling.
- **`test_health.py`** — health service and route.

### 2. Scenario tests

These live in **`test_client_flow.py`**. Each test is a single function that walks through a realistic sequence of operations where later steps depend on earlier ones — closer to how a real user (or another service) would interact with the API.

State still resets between scenarios, but *within* a scenario, state accumulates.

The three scenarios:

1. **`TestClientLifecycleFlow`** — full create → read → update → delete journey. Confirms the new client appears in the list, partial updates preserve untouched fields, and after deletion the list size goes back to the seed count.

2. **`TestMultiClientFlow`** — mixes operations across seeded and new clients: creates two new clients, renames a seeded one, deletes one of the new ones, then asserts the combined final state (counts, names, what survived, what didn't).

3. **`TestPaymentProgressionFlow`** — a "billing then payment" sequence on a client that starts with `latest_transaction_date = None`. First bumps `billed_amount`, then on a later PATCH records a payment plus a transaction timestamp, and verifies the earlier billing change is still there.

## How to run tests manually

From the project root, with the venv active:

```bash
# everything
pytest

# just the flow tests
pytest tests/test_client_flow.py -v

# a single class
pytest tests/test_client_flow.py::TestClientLifecycleFlow -v

# a single test
pytest tests/test_client_flow.py::TestClientLifecycleFlow::test_create_read_update_delete -v


## How tests run in CI (GitHub Actions)

CI is defined in [.github/workflows/ci.yml](.github/workflows/ci.yml). On every **push to `main`** and every **pull request targeting `main`**, GitHub Actions:

1. Checks out the code.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt` (with pip caching).
4. Runs `pytest -v`.

You can see the run in the **Actions** tab of the GitHub repo. A green check on a PR means the suite passed; a red X blocks the PR.

### Running the CI workflow locally (optional)

GitHub Actions itself runs only on GitHub, but can simulate it locally with [`act`](https://github.com/nektos/act)
```bash
# install (macOS)
brew install act

# run the workflow
act push
```

However for day-to-day development, just running `pytest` locally is faster.



Please note: Some content of code (boilerplate and small portion of logic) and documentation has been generated using Claude code AI.
