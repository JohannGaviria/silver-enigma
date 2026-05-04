# Technical Decisions — Silver Enigma

Architecture Decision Records (ADRs). Each decision documents the context, alternatives, and final reasoning.

> This document answers: **"why was it built this way?"**

---

## ADR-001: SELECT FOR UPDATE for stock reservation

### Context

Multiple buyers may confirm orders for the same product simultaneously. The system must guarantee that stock is never oversold.

### Considered alternatives

- **Optimistic locking** (version column): cheap reads, retries on write conflicts
- **SELECT FOR UPDATE** (pessimistic locking): locks row during read
- **Redis as distributed mutex**: external lock before touching DB
- **Queue-based confirmation**: Celery to serialize processing

### Decision: SELECT FOR UPDATE

- The database is the bottleneck anyway — PostgreSQL row locks are cheap
- No additional infrastructure dependency required (Redis already exists but is not needed here)
- Order confirmation is fast (< 50ms), so locks don't create long queues
- Optimistic locking introduces retry logic on the client → higher complexity
- This is the standard approach in inventory and B2B systems

> **Accepted trade-off:** lower throughput under extreme load. For Silver Enigma's scale, this is acceptable.

---

## ADR-002: Why stock_available is NOT cached

### Context

Stock is the most critical piece of data. Caching it seems attractive to reduce database load.

### Why it is not cached

- Stock changes on every confirmation, cancellation, and dispatch
- A stale cache value could allow overselling inventory
- Eventual consistency is **not acceptable** in a fulfillment system
- Buyers see real-time availability — stale data directly reduces trust

### What IS cached and why

- `cache:warehouses_by_supplier` — rarely changing, non-critical data
- `cache:refresh_token` — naturally TTL-based data, fits Redis perfectly

> **Rule:** only cache data whose staleness cannot cause inventory inconsistency or security issues.

---

## ADR-003: Modular monolith instead of microservices

### Context

The system could be split into microservices (auth, order, inventory).

### Decision: Modular monolith

- Atomic consistency between order state changes and stock movements requires a **single DB transaction**
- Microservices would require sagas or 2PC → high complexity overhead
- Single-team development — no benefit from independent deployments
- Modular structure allows future extraction into microservices if needed
- Easier to test, debug, and reason about

> A modular monolith is the correct default until there is a **measured, real scaling need** for separation.

---

## ADR-004: Hexagonal Architecture (Ports & Adapters)

### Context

A simpler approach could be FastAPI + SQLAlchemy directly inside routers.

### Decision: Hexagonal Architecture

- Enables testing use cases with `FakeRepositories` without a real DB — fast unit tests
- Keeps domain logic isolated — the most stable part of the system
- Infrastructure (DB, external services) can be replaced without touching the domain layer
- Prevents "God services" that grow into unmaintainable files
- A widely adopted pattern in production Python systems

### Trade-off

More boilerplate (ports, DTOs, use cases), justified by domain complexity and long-term maintainability.

---

## ADR-005: Redis-backed opaque refresh tokens vs JWT

### Context

Refresh tokens could be JWTs (self-contained) or opaque tokens stored server-side.

### Decision: opaque tokens in Redis

- JWT refresh tokens cannot be revoked without maintaining a blacklist
- Logout must be immediate and reliable → requires server-side invalidation
- Token rotation is straightforward: consume → invalidate → issue new token
- Redis TTL naturally models token expiration

### Access token remains JWT

Access tokens are short-lived (10 minutes), making revocation less critical and acceptable.

---

## ADR-006: Celery + Redis for asynchronous notifications

### Context

Notifications could be sent synchronously within the request lifecycle.

### Decision: Celery async processing

- API response should not wait for email delivery
- Notification failures must not affect order transaction success
- Built-in retry with exponential backoff reduces custom error handling
- Redis is already part of the infrastructure

### Critical guarantee

> Celery tasks are enqueued **only after transaction commit**.
> If the commit fails, no notification is queued — preventing inconsistent messaging.

---

## ADR-007: UUID primary keys instead of SERIAL/BIGINT

### Decision

All entities use UUID v4 as primary keys.

### Reasons

- Prevents ID enumeration (improves security against IDOR attacks)
- Enables ID generation at application level without DB round-trips
- Easier future replication or distributed architecture
- Performance overhead compared to BIGINT is acceptable at this scale

---

## ADR-008: Unit of Work pattern for transaction management

### Context

Before introducing the Unit of Work (UoW) pattern, use cases received repository instances directly and relied on each repository adapter to call `session.commit()` internally. This created several problems:

- **No atomic multi-repository writes**: if a use case interacted with two repositories, there was no guarantee that both writes would be committed together or not at all.
- **Session lifecycle ambiguity**: the session was created outside the use case, but committed inside a repository — making ownership unclear and rollback difficult.
- **Poor unit testability**: mocking individual repositories worked, but there was no single seam to verify that the whole interaction (read → write → commit) happened atomically.

### Considered alternatives

- **Keep per-repository commits**: simple, but fundamentally unsafe for multi-step operations.
- **Pass the session to the use case**: use case would call `session.commit()` directly — couples application layer to SQLAlchemy.
- **Middleware / dependency-injection-level transaction**: a FastAPI dependency opens and closes the session around each request — hard to test and forces one transaction per HTTP request regardless of use-case needs.
- **Unit of Work pattern**: application layer depends only on an abstract `UnitOfWorkPort`; infrastructure provides the SQLAlchemy implementation.

### Decision: Unit of Work port per bounded context

Each module defines its own `<Entity>UnitOfWorkPort` (e.g., `UserUnitOfWorkPort`) that:

1. Extends the shared base `UnitOfWorkPort` (async context manager with `commit` / `rollback`).
2. Declares the module's repositories as typed attributes (e.g., `users: UserRepositoryPort`).

The infrastructure layer provides a `SQLAlchemy<Entity>UnitOfWorkAdapter` that:

1. Creates a fresh `AsyncSession` on `__aenter__`.
2. Binds all module repositories to that single session.
3. Rolls back automatically on unhandled exceptions in `__aexit__`.
4. Exposes explicit `commit()` and `rollback()` methods for the use case to call.

### Key design choices

- **Domain validation before the UoW opens**: Value Objects are constructed (and validated) before `async with unit_of_work`. Invalid input never opens a session.
- **Explicit commit**: the UoW never auto-commits on clean exit. The use case must call `await uow.commit()` — making the intent visible in code.
- **One session per use case execution**: the session factory creates a new session on every `__aenter__`, guaranteeing isolation between concurrent requests.
- **Unit tests mock the entire UoW**: a `MagicMock` configured as an async context manager replaces the real adapter — no database required for use-case tests.
- **Integration tests validate the adapter contract**: `commit`, `rollback`, auto-rollback on exception, and session isolation are all tested against a real PostgreSQL instance.

### Naming convention

| Artifact        | Location                                                                                       | Example                           |
|-----------------|------------------------------------------------------------------------------------------------|-----------------------------------|
| Base UoW port   | `shared/domain/ports/unit_of_work/unit_of_work_port.py`                                        | `UnitOfWorkPort`                  |
| Module UoW port | `<module>/domain/ports/unit_of_work/<entity>_unit_of_work_port.py`                             | `UserUnitOfWorkPort`              |
| UoW adapter     | `<module>/infrastructure/persistence/unit_of_work/sqlalchemy_<entity>_unit_of_work_adapter.py` | `SQLAlchemyUserUnitOfWorkAdapter` |

### Trade-off

Additional indirection (one more port + adapter per module). Justified because:

- Use cases remain framework-agnostic and trivially testable.
- Transaction atomicity is guaranteed by design, not by convention.
- The pattern scales cleanly as more repositories are added to a module.
