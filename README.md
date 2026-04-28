# Silver Enigma

**Silver Enigma** is a B2B order management engine focused on **inventory consistency, fulfillment traceability, and concurrency control** in distribution chains (supplier → warehouse → store).

Unlike traditional e-commerce systems, this is not a shopping cart solution — it is a **state-driven fulfillment engine** where every order transition directly impacts stock.

**Problem**

In B2B distribution, the main challenge is not knowing if stock exists, but understanding:

- How much stock is available
- How much is already committed to active orders

Without this distinction, multiple buyers can purchase the same units simultaneously, leading to:

- Unfulfillable orders
- Loss of trust
- Contractual penalties
- Operational chaos


**Solution**

Silver Enigma introduces an explicit reservation model to guarantee inventory consistency:

- Total Stock → Physical units in warehouse
- Reserved Stock → Units committed to confirmed orders
- Available Stock → Units that can still be purchased

```python
available_stock = total_stock - reserved_stock
```

All operations affecting stock are executed atomically, ensuring that inventory is never overcommitted — even under concurrent requests.

**Key Insight**

The core problem is not stock — it is commitment visibility.

Silver Enigma ensures that:

> Stock is not just tracked — it is accurately allocated in real time.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technologies](#technologies)
- [Quickstart](#quickstart)
   - [Clone the repository](#clone-the-repository)
   - [Copy environment variables](#copy-environment-variables)
   - [Run in a Docker environment](#run-in-a-docker-environment)
- [Development Guide](#development-guide)
- [API Endpoints](#api-endpoints)
   - [Authentication and Users Module](#authentication-and-users-module)
   - [Warehouse Management](#warehouse-management)
   - [Products & Inventory Management](#products--inventory-management)
   - [Orders Management](#orders-management)
   - [System](#system)
- [Notifications (Domain Triggers)](#notifications-domain-triggers)
- [Testing](#testing)
- [DevOps](#devops)
- [Design Decisions](#design-decisions)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Architecture Overview

Silver Enigma follows a modular monolith architecture using the Hexagonal (Ports & Adapters) pattern.

The system is structured into:

- Domain: core business logic and rules
- Application: use cases orchestrating domain operations
- Infrastructure: database, cache, messaging systems
- Presentation: HTTP layer (FastAPI) and Triggers

This separation ensures that business logic remains independent from external systems.

See full architecture documentation: [Architecture](./docs/architecture.md)

---

## Technologies

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/doc/)[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)[![REST API](https://img.shields.io/badge/REST_API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://restfulapi.net/)[![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white)](https://jinja.palletsprojects.com/)[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/)[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/docs/)[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)[![Alembic](https://img.shields.io/badge/Alembic-3D3D3D?style=for-the-badge&logo=alembic&logoColor=white)](https://alembic.sqlalchemy.org/)[![PyJWT](https://img.shields.io/badge/PyJWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://pyjwt.readthedocs.io/)[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)[![Ruff](https://img.shields.io/badge/Ruff-000000?style=for-the-badge&logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)[![mypy](https://img.shields.io/badge/mypy-233564?style=for-the-badge&logo=mypy&logoColor=white)](https://mypy.readthedocs.io/)[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/)[![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://swagger.io/docs/)[![Structlog](https://img.shields.io/badge/Structlog-000000?style=for-the-badge&logo=logstash&logoColor=white)](https://www.elastic.co/guide/en/logstash/current/index.html)[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://docs.github.com/actions)[![CI/CD](https://img.shields.io/badge/CI%2FCD-000000?style=for-the-badge&logo=github&logoColor=white)](https://about.gitlab.com/topics/ci-cd/)[![PyTest](https://img.shields.io/badge/PyTest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)[![Monolith](https://img.shields.io/badge/Monolith-6C63FF?style=for-the-badge)](https://en.wikipedia.org/wiki/Monolithic_application)[![Hexagonal Architecture](https://img.shields.io/badge/Hexagonal-FFB300?style=for-the-badge)](https://en.wikipedia.org/wiki/Hexagonal_architecture)

---

## Quickstart

### Clone the repository

```bash
git clone git@github.com:JohannGaviria/silver-enigma.git
cd silver-enigma
```

### Copy environment variables

Copy `.env.example` to `.env` and edit as needed, or set the variables directly in your environment. See the table below for required variables.

```bash
cp .env.example .env
```

| Category                   | Key                          | Description                       | Example                                                             |
| -------------------------- | ---------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| Application Metadata       | APP_NAME                     | Application name                  | Silver Enigma                                                       |
| Application Metadata       | APP_SUMMARY                  | Application summary               | B2B order management engine                                         |
| Application Metadata       | APP_DESCRIPTION              | Application description           | State-driven fulfillment engine                                     |
| Backend Configuration      | DEBUG                        | Debug mode                        | True                                                                |
| Backend Configuration      | ENVIRONMENT                  | Environment                       | development                                                         |
| Backend Configuration      | BACKEND_PORT                 | Backend port                      | 8000                                                                |
| Backend Configuration      | BACKEND_WORKERS              | Backend workers                   | 4                                                                   |
| Backend Configuration      | CORS_ALLOW_ORIGINS           | Allowed frontend origins          | https://app.midominio.com,https://admin.midominio.com               |
| Backend Configuration      | CORS_ALLOW_CREDENTIALS       | Allow cookies/auth credentials    | True                                                                |
| Database Configuration     | DATABASE_URL                 | Database URL                      | postgresql+asyncpg://postgres:password@postgres:5432/silver_enigma  |
| Database Configuration     | DATABASE_URL_ALEMBIC         | Database URL for alembic          | postgresql+psycopg2://postgres:password@postgres:5432/silver_enigma |
| Database Configuration     | DB_HOST                      | Database host                     | postgres                                                            |
| Database Configuration     | DB_PORT                      | Database port                     | 5432                                                                |
| Database Configuration     | POSTGRES_USER                | PostgreSQL user                   | postgres                                                            |
| Database Configuration     | POSTGRES_DB                  | PostgreSQL database               | silver_enigma                                                       |
| Database Configuration     | POSTGRES_PASSWORD            | PostgreSQL password               | password                                                            |
| Redis Configuration        | REDIS_PORT                   | Redis port                        | 6379                                                                |
| Redis Configuration        | REDIS_PASSWORD               | Redis password                    | password                                                            |
| Redis Configuration        | REDIS_HOST                   | Redis host                        | redis                                                               |
| Redis Configuration        | REDIS_DB                     | Redis database                    | 0                                                                   |

---

### Run in a Docker environment

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

#### Running the Service with Docker

You can easily start the backend, database, and other services using Docker Compose:

```bash
docker compose up --build
```

Alternatively, if you prefer using the Makefile:

```bash
make up
```

Once the services are running, the API will be accessible at:

[http://localhost:8000/docs](http://localhost:8000/docs) – this provides the **interactive Swagger UI** for testing all endpoints.

---

## Development Guide

For a complete guide on how to work with the project locally, including:

- environment setup
- running services (Docker / non-Docker)
- database migrations
- testing strategy
- linting and type checking
- naming conventions

See the full documentation here: [Development Guide](./docs/development.md)

---

## API Endpoints

### Authentication and Users Module

| Method | Endpoint                  | Requires Auth | Roles                        | Description                                        |
|--------|---------------------------|---------------|------------------------------|----------------------------------------------------|
| `POST` | `/api/v1/auth/register`   | Yes           | `ADMIN`                      | Register a new user                                |
| `POST` | `/api/v1/auth/login`      | No            | —                            | Authenticate user and return access/refresh tokens |
| `POST` | `/api/v1/auth/refresh`    | No            | —                            | Rotate refresh token and issue new credentials     |
| `POST` | `/api/v1/auth/logout`     | Yes           | `SUPPLIER`, `BUYER`, `ADMIN` | Invalidate active refresh token (logout)           |

### Warehouse Management

| Method  | Endpoint                                     | Requires Auth | Roles      | Description                        |
|---------|----------------------------------------------|---------------|------------|------------------------------------|
| `POST`  | `/api/v1/warehouses`                         | Yes           | `SUPPLIER` | Create a new warehouse             |
| `GET`   | `/api/v1/warehouses`                         | Yes           | `SUPPLIER` | List supplier warehouses           |
| `PATCH` | `/api/v1/warehouses/{warehouse_id}`          | Yes           | `SUPPLIER` | Update warehouse information       |
| `PATCH` | `/api/v1/warehouses/{warehouse_id}/status`   | Yes           | `SUPPLIER` | Activate or deactivate a warehouse |

### Products & Inventory Management

| Method  | Endpoint                                                        | Requires Auth | Roles      | Description                         |
|---------|-----------------------------------------------------------------|---------------|------------|-------------------------------------|
| `POST`  | `/api/v1/products`                                              | Yes           | `SUPPLIER` | Create a product                    |
| `PATCH` | `/api/v1/products/{product_id}`                                 | Yes           | `SUPPLIER` | Update product information          |
| `PATCH` | `/api/v1/products/{product_id}/status`                          | Yes           | `SUPPLIER` | Activate or deactivate a product    |
| `PUT`   | `/api/v1/warehouses/{warehouse_id}/products/{product_id}/stock` | Yes           | `SUPPLIER` | Register or adjust product stock    |
| `GET`   | `/api/v1/warehouses/{warehouse_id}/products/stock`              | Yes           | `SUPPLIER` | Retrieve stock status per warehouse |
| `GET`   | `/api/v1/products`                                              | Yes           | `BUYER`    | Retrieve available product catalog  |

### Orders Management

| Method  | Endpoint                            | Requires Auth | Roles               | Description                                       |
|---------|-------------------------------------|---------------|---------------------|---------------------------------------------------|
| `POST`  | `/api/v1/orders`                    | Yes           | `BUYER`             | Create a purchase order in DRAFT state            |
| `POST`  | `/api/v1/orders/{order_id}/confirm` | Yes           | `BUYER`             | Confirm order and reserve stock                   |
| `POST`  | `/api/v1/orders/{order_id}/process` | Yes           | `SUPPLIER`          | Move order to PROCESSING state                    |
| `POST`  | `/api/v1/orders/{order_id}/ship`    | Yes           | `SUPPLIER`          | Mark order as SHIPPED and update stock            |
| `POST`  | `/api/v1/orders/{order_id}/deliver` | Yes           | `SUPPLIER`          | Mark order as DELIVERED                           |
| `POST`  | `/api/v1/orders/{order_id}/cancel`  | Yes           | `BUYER`, `SUPPLIER` | Cancel order and release reserved stock if needed |
| `GET`   | `/api/v1/orders/{order_id}`         | Yes           | `BUYER`, `SUPPLIER` | Retrieve full order details                       |
| `GET`   | `/api/v1/orders`                    | Yes           | `BUYER`, `SUPPLIER` | List orders with filters and pagination           |

### System

| Method  | Endpoint     | Requires Auth | Roles | Description                               |
|---------|--------------|---------------|-------|-------------------------------------------|
| `GET`   | `/`          | No            | —     | Welcome endpoint root                     |
| `GET`   | `/docs`      | No            | —     | Swagger UI for API documentation          |
| `GET`   | `/health`    | No            | —     | Health check for API, database, and Redis |

---

## Notifications (Domain Triggers)

| Trigger Event                          | Description                                          |
| -------------------------------------- | ---------------------------------------------------- |
| Order created                          | Notify supplier when a buyer creates a new order     |
| Order confirmed                        | Notify buyer when order is confirmed                 |
| Order shipped                          | Notify buyer when order is shipped                   |
| Order delivered                        | Notify buyer when order is delivered                 |
| Order cancelled                        | Notify buyer or supplier depending on actor          |
| Order cancelled (from CONFIRMED state) | Notify supplier when buyer cancels a confirmed order |

---

## Testing

The project includes:

- Unit tests for domain logic and use cases
- Integration tests for infrastructure and API endpoints
- E2E tests for complete user workflows across the system, validating real-world scenarios from request to persistence and response

Run tests:

```bash
make test
```

See testing strategy: [Testing](./docs/testing-strategy.md)

---

## DevOps

The DevOps strategy for **Silver Enigma** ensures fast, reliable, and reproducible deployments. It leverages containerization, CI/CD pipelines, and environment management to streamline the software lifecycle.

### Key Components

1. **Containerization**
   - Dockerized services for consistent environments
   - `docker-compose.yml` for local orchestration

2. **Continuous Integration (CI)**
   - Automated pipelines for linting, testing, and validation
   - Ensures code quality before merging

3. **Continuous Deployment (CD)**
   - Automated deployment pipelines for staging and production
   - Rolling updates and versioned Docker images

4. **Environment Management**
   - `.env` files for local development
   - Secrets managed via GitHub Secrets for CI/CD

See DevOps full documentation: [DevOps Documentation](./docs/devops.md).

---

## Design Decisions

Key decisions in this project:

- Modular monolith instead of microservices to reduce complexity
- Strong consistency for stock operations
- PostgreSQL for transactional guarantees

These decisions prioritize correctness and consistency over premature scalability.

See full decisions log: [Design Decisions](./docs/decisions.md)

---

## Future Improvements

- Idempotency for critical operations (order confirmation)
- Event-driven architecture for stock movements
- CQRS for read/write separation
- Distributed locking strategies

---

## License

Distributed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

> Made with ♥️ by [JohannGaviria](https://github.com/JohannGaviria) – always happy to connect for feedback, collaboration, or job opportunities.
