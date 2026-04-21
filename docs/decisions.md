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
- Order confirmation is fast (< 50ms), so locks don’t create long queues
- Optimistic locking introduces retry logic on the client → higher complexity
- This is the standard approach in inventory and B2B systems

> **Accepted trade-off:** lower throughput under extreme load. For Silver Enigma’s scale, this is acceptable.

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
- Prevents “God services” that grow into unmaintainable files
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
