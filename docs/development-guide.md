# Development Guide — Silver Enigma

> B2B order engine with stock control and fulfillment traceability.
> Stack: Python 3.12 · FastAPI · PostgreSQL · Redis · Celery · Docker

---

## Table of contents

1. [Clone the repository](#1-clone-the-repository)
2. [Dependency management with Poetry](#2-dependency-management-with-poetry)
3. [Run the environment](#3-run-the-environment)
   - [Without Docker](#31-run-the-environment-without-docker)
   - [With Docker](#32-run-the-environment-with-docker)
4. [PostgreSQL](#4-postgresql)
5. [Redis](#5-redis)
6. [Tests](#6-tests)
   - [With Docker](#61-tests-with-docker-recommended)
   - [Without Docker](#62-tests-without-docker-unit-only)
7. [Linting and type checking — Ruff + Mypy](#7-linting-and-type-checking--ruff--mypy)
8. [Naming conventions](#8-naming-conventions)

---

## 1. Clone the repository

```bash
git clone https://github.com/JohannGaviria/silver-enigma.git
cd silver-enigma
```

Copy the environment variables file and fill it in with your local values:

```bash
cp .env.example .env
```

Generate the `SECRET_KEY` for JWT:

```bash
openssl rand -hex 32
```

Paste the output into `.env`.

> **Never** commit the real `.env` file. It is already excluded via `.gitignore`.

---

## 2. Dependency management with Poetry

Silver Enigma uses [Poetry](https://python-poetry.org/) as its dependency manager and virtual environment tool.

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify it is available on your PATH:

```bash
poetry --version
# Poetry (version 2.3.4)
```

### Install project dependencies

```bash
poetry install
```

Or using the Makefile:

```bash
make setup
```

> **Note:** running this command will also install the pre-commit hooks.

This creates an isolated virtual environment and installs all dependencies defined in `pyproject.toml`, including development tools (`ruff`, `mypy`, `pytest`, etc.).

### Useful Poetry commands

```bash
# Add a production dependency
poetry add fastapi

# Add a development-only dependency
poetry add --group dev pytest-asyncio

# Display the dependency tree
poetry show --tree

# Update dependencies while respecting pyproject.toml constraints
poetry update
```

---

## 3. Run the environment

### 3.1 Run the environment without Docker

If you prefer to run the API directly with Poetry and manage external services (PostgreSQL and Redis) separately:

#### Requirements

- [Python 3.12](https://www.python.org/downloads/release/python-3120/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Redis](https://redis.io/docs/latest/)

#### Start the API

```bash
poetry shell
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.2 Run the environment with Docker

Docker Compose starts all required services together: the API, the Celery worker, PostgreSQL, and Redis.

#### Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 24, or Docker Engine + Compose plugin ≥ 2.24

#### Start the full stack

```bash
docker compose up --build
```

Or using the Makefile:

```bash
make up
```

The first run downloads the base images and builds the application image. Subsequent runs are significantly faster if dependencies have not changed.

The API is available at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`.

### Common commands

```bash
# Run in the background
docker compose up -d

# Tail logs for a specific service
docker compose logs -f backend
docker compose logs -f postgres

# Rebuild only the application image (e.g., after changing dependencies)
docker compose build backend

# Stop all services
docker compose down  # or: make down

# Stop all services and remove volumes (deletes the database)
docker compose down -v

# Check the status of all services
docker compose ps
```

---

## 4. PostgreSQL

### Direct connection

```bash
# From the host (requires psql to be installed)
psql postgresql://postgres:password@postgres:5432/silver_enigma

# From inside the container
docker compose exec postgres psql -U postgres -d silver_enigma
```

### Migrations with Alembic

Silver Enigma uses Alembic to version the database schema. All migrations are stored in `alembic/versions/` and are fully reversible.

```bash
# Apply all pending migrations
alembic upgrade head

# Revert the last migration
alembic downgrade -1

# Revert to a specific revision
alembic downgrade <revision_id>

# View the full migration history
alembic history --verbose

# Show the currently applied migration
alembic current
```

### Create a new migration

Always generate migrations from SQLAlchemy models rather than writing them by hand:

```bash
alembic revision --autogenerate -m "add_notifications_table"
```

Review the generated file in `alembic/versions/` before applying it, and make sure the `downgrade()` function is correct.

### Migration rules

- Every migration must implement both `upgrade()` and `downgrade()`.
- Indexes must be created through migrations, never applied manually.
- Migrations run automatically when the API container starts (`alembic upgrade head` is defined in the `command` of `docker-compose.yml`).
- Never modify a migration that has already been applied to `main`. Create a new one instead.

---

## 5. Redis

Silver Enigma uses Redis for three distinct purposes:

| Purpose          | Key pattern                         | TTL                   |
|------------------|-------------------------------------|-----------------------|
| Refresh tokens   | `cache:refresh_token:<token>`       | 3 days                |
| Warehouse cache  | `cache:warehouses_by_supplier:<id>` | System-defined policy |
| Celery broker    | Database `1` (`/1`)                 | Managed by Celery     |

### Direct connection

```bash
# From the host (requires redis-cli to be installed)
redis-cli -h localhost -p 6379

# From inside the container
docker compose exec redis redis-cli
AUTH password
```

### Useful redis-cli commands

```bash
# List all active keys
KEYS *

# Inspect a specific refresh token
GET cache:refresh_token:<token>

# Check the remaining TTL of a key
TTL cache:refresh_token:<token>

# Manually delete a key (useful during development)
DEL cache:refresh_token:<token>

# Display general server information
INFO server

# Flush database 0 (use with caution in production!)
FLUSHDB
```

### Health check

The application exposes a `/health` endpoint that verifies connectivity with both Redis and PostgreSQL:

```bash
curl http://localhost:8000/health
# {"status": "ok", "postgres": "up", "redis": "up"}
```

---

## 6. Tests

The project has three types of tests, organized into separate directories:

```
tests/
├── unit/          # No DB or Redis. Uses FakeRepositories. Very fast.
├── integration/   # Uses a real PostgreSQL instance. Tests repositories and concurrency.
└── e2e/           # Full HTTP flows against the running application.
```

### 6.1 Tests with Docker (recommended)

Docker Compose uses an isolated database for tests, preventing any interference with the development database.

```bash
# Run all tests (unit + integration + e2e)
docker compose run --rm backend pytest

# Run only integration tests
docker compose run --rm backend pytest tests/integration/ -v

# Run only e2e tests
docker compose run --rm backend pytest tests/e2e/ -v

# Run with coverage report
docker compose run --rm backend pytest --cov=src --cov-report=term-missing

# Run a specific test by name
docker compose run --rm backend pytest -k "test_concurrent_order_confirmation"

# Stop on the first failure
docker compose run --rm backend pytest -x
```

To run integration and e2e tests, the infrastructure services must be running first:

```bash
docker compose up db redis -d
pytest tests/integration/ -m db
pytest tests/e2e/ -m e2e
```

### 6.2 Tests without Docker (unit only)

Unit tests have no external dependencies and can be run directly with Poetry:

```bash
# Run only unit tests
poetry run pytest tests/unit/ -v

# Run with coverage report
poetry run pytest tests/unit/ --cov=src --cov-report=term-missing

# Run in watch mode (requires pytest-watch)
poetry run ptw tests/unit/
```

Unit tests use `FakeRepositories` that implement the same ports (ABCs) as the real repositories:

```python
# tests/unit/conftest.py
class FakeOrderRepository(IOrderRepository):
    def __init__(self):
        self.orders: dict = {}

    async def get_order_for_update(self, order_id: UUID) -> Order | None:
        return self.orders.get(order_id)

    async def save(self, order: Order) -> None:
        self.orders[order.id] = order
```

---

## 7. Linting and type checking — Ruff + Mypy

### Ruff (linter + formatter)

[Ruff](https://docs.astral.sh/ruff/) replaces flake8, isort, and black in a single, extremely fast binary.

```bash
# Check for linting errors
poetry run ruff check .

# Auto-fix issues that Ruff can resolve
poetry run ruff check . --fix

# Format the code (equivalent to black)
poetry run ruff format .

# Check formatting without modifying files (useful in CI)
poetry run ruff format . --check
```

### Mypy (static type checking)

[Mypy](https://mypy.readthedocs.io/) verifies that types are used correctly throughout the codebase.

```bash
# Type-check the entire project
poetry run mypy src/

# Type-check a specific module
poetry run mypy src/modules/orders/

# Generate a type coverage report
poetry run mypy src/ --any-exprs-report .
```

### Run everything together (pre-commit / CI)

```bash
ruff check . && ruff format . --check && mypy src/
```

Or using a single Makefile command:

```bash
# Format and auto-fix code
make format

# Check without modifying files
make check

# Lint and type-check
make lint
```

### Pre-commit hooks (optional but recommended)

```bash
# Install hooks in the local repository
pre-commit install
```

> **Note:** if you already ran `make setup`, the pre-commit hooks have been installed automatically.

---

## 8. Naming conventions

The following rules ensure consistency across the entire codebase.

### Files

| Type                        | Convention                                | Example                                  |
|-----------------------------|-------------------------------------------|------------------------------------------|
| Entity (Domain)             | `<aggregate>_entity.py`                   | `order_entity.py`                        |
| Value Object (Domain)       | `<concept>_vo.py`                         | `stock_vo.py`                            |
| Repository Port (Domain)    | `<aggregate>_repository_port.py`          | `order_repository_port.py`               |
| Outbound Port (Domain)      | `<action>_outbound_port.py`               | `notification_outbound_port.py`          |
| Domain Service              | `<aggregate>_service.py`                  | `order_service.py`                       |
| Domain event                | `<action>_<aggregate>_event.py`           | `confirm_order_event.py`                 |
| Domain Exception            | `<aggregate>_exception.py`                | `order_exception.py`                     |
| Use Case (Application)      | `<action>_<aggregate>_use_case.py`        | `confirm_order_use_case.py`              |
| DTO (Application)           | `<action>_<aggregate>_dto.py`             | `confirm_order_dto.py`                   |
| Mapper (Infrastructure)     | `<aggregate>_persistence_mapper.py`       | `order_persistence_mapper.py`            |
| ORM Model (Infrastructure)  | `<aggregate>_model.py`                    | `order_model.py`                         |
| Repo Adapter (Infra)        | `<orm>_<aggregate>_repository_adapter.py` | `sqlalchemy_order_repository_adapter.py` |
| External Adapter (Infra)    | `<tech>_<purpose>_adapter.py`             | `smtp_notification_email_adapter.py`     |
| Composition (Presentation)  | `<use_case>_composition.py`               | `confirm_order_use_case_composition.py`  |
| Dependency wiring           | `<aggregate>_composition.py`              | `order_repository_composition.py`        |
| Exception Handlers (API)    | `<aggregate>_exception_handlers.py`       | `order_exception_handlers.py`            |
| Schema                      | `<action>_<aggregate>_schema.py`          | `confirm_order_schema.py`                |
| Router (API)                | `<action>_<aggregate>_router.py`          | `confirm_order_router.py`                |
| Mapper (Presentation)       | `<aggregate>_api_mapper.py`               | `order_api_mapper.py`                    |

### Classes

| Type                    | Convention                           | Example                            |
|-------------------------|--------------------------------------|------------------------------------|
| Entity                  | `<Aggregate>Entity`                  | `OrderEntity`                      |
| Value Object            | `<Concept>VO`                        | `StockVO`                          |
| Repository Port         | `<Aggregate>RepositoryPort`          | `OrderRepositoryPort`              |
| Outbound Port           | `<Action>OutboundPort`               | `NotificationOutboundPort`         |
| Domain Service          | `<Aggregate>Service`                 | `OrderService`                     |
| Domain Event            | `<Action><Aggregate>Event`           | `ConfirmOrderService`              |
| Exception               | `<Aggregate>Exception`               | `OrderException`                   |
| Use Case                | `<Action><Aggregate>UseCase`         | `ConfirmOrderUseCase`              |
| Command (DTO in)        | `<Action><Aggregate>CommandDto`      | `ConfirmOrderCommandDto`           |
| Response (DTO out)      | `<Action><Aggregate>ResponseDto`     | `ConfirmOrderResponseDto`          |
| ORM Model               | `<Aggregate>Model`                   | `OrderModel`                       |
| Persistence Mapper      | `<Aggregate>PersistenceMapper`       | `OrderPersistenceMapper`           |
| Repo Adapter            | `<Tech><Aggregate>RepositoryAdapter` | `SQLAlchemyOrderRepositoryAdapter` |
| External Adapter        | `<Tech><Purpose>Adapter`             | `SMTPNotificationEmailAdapter`     |
| Schema Request          | `<Action><Aggregate>RequestSchema`   | `ConfirmOrderRequestSchema`        |
| Schema Response         | `<Action><Aggregate>ResponseSchema`  | `ConfirmOrderResponseSchema`       |
| Router                  | `<Aggregate>Router`                  | `OrderRouter`                      |
| API Mapper              | `<Aggregate>APIMapper`               | `OrderAPIMapper`                   |
| Exception Handler       | `<Aggregate>ExceptionHandler`        | `OrderExceptionHandler`            |
| Use Case Composition    | `<Action><Aggregate>Composition`     | `ConfirmOrderComposition`          |

### Variables and functions

```python
# Variables and parameters: snake_case
order_id: UUID
buyer_id: UUID
available_stock: int

# Functions and methods: snake_case, verb first
async def get_order_for_update(order_id: UUID) -> Order: ...
async def reserve_atomic(items: list[OrderItem]) -> None: ...
async def record_stock_movements(movements: list[StockMovement]) -> None: ...

# Module-level constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_PAGE_SIZE = 20

# Enums: PascalCase for the class, SCREAMING_SNAKE_CASE for values
class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class StockMovementType(str, Enum):
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    DECREMENT = "DECREMENT"
    ADJUST = "ADJUST"
```

### Additional rules

- Use case methods are always named `execute()`.
- Repository methods use descriptive verbs: `get_by_id()`, `get_order_for_update()`, `save()`, `list_by_buyer()`.
- Ports (ABCs) contain no logic — only abstract method signatures decorated with `@abstractmethod`.
- Domain exceptions must inherit from the `DomainError(Exception)` base class.
- Domain events are immutable dataclasses (`@dataclass(frozen=True)`).
- Never use `id` as a variable name, as it shadows the Python built-in. Use `order_id`, `user_id`, etc. instead.
