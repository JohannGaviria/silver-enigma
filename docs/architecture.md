# Architecture — Silver Enigma

> Defines how the system is organized, how dependencies flow, and how separation of concerns is maintained to ensure scalability, maintainability, and consistency.

---

## Table of Contents

1. [Overview](#1-overview)
2. [High-Level Structure](#2-high-level-structure)
3. [Architectural Layers](#3-architectural-layers)

   - [Domain Layer (Core)](#4-domain-layer-core)
   - [Application Layer](#5-application-layer)
   - [Infrastructure Layer](#6-infrastructure-layer)
   - [Presentation Layer](#7-presentation-layer)
4. [Detailed Example — Orders Module](#8-detailed-example--orders-module)
5. [Dependency Flow](#9-dependency-flow)
6. [Shared Module](#10-shared-module)
7. [Module Communication](#11-module-communication)
8. [Request Flow (End-to-End)](#12-request-flow-end-to-end)
9. [Unit of Work Pattern](#13-unit-of-work-pattern)
10. [Key Benefits](#14-key-benefits)
11. [Architectural Decisions](#15-architectural-decisions)
12. [When to Extract Microservices](#16-when-to-extract-microservices)
13. [Summary](#17-summary)

---

## 1. Overview

**Silver Enigma** is designed using:

- **Domain-Driven Design (DDD)**
- **Clean Architecture (Ports & Adapters)**
- **Modular Monolith (domain-based)**
- **Unit of Work (transaction boundary management)**

The system is organized into **independent domain-based modules**, where each module encapsulates its own business logic, infrastructure, and exposure.

---

## 2. High-Level Structure

```
src/
| └── modules/
|   ├── auth/
|   ├── warehouses/
|   ├── products/
|   ├── orders/
|   └── notifications/
shared/
```

### Key Principles

- **High cohesion within modules**
- **Low coupling between modules**
- **Dependencies point inward (domain-first)**
- **The domain does not depend on frameworks**
- **Transactions are managed at the application layer via Unit of Work**

---

## 3. Architectural Layers

Each module follows the same structure:

```
application/
domain/
infrastructure/
presentation/
```

---

### 4. Domain Layer (Core)

> The core of the system. Contains pure business logic.

#### Contains:

- **Entities** → Models with identity and rules
- **Value Objects** → Immutable types
- **Domain Services** → Complex logic across entities
- **Domain Events** → Business events
- **Ports (Interfaces):**

  - Repositories
  - Unit of Work (transaction boundary)
  - External services (outbound)
- **Exceptions** → Domain rules

#### Rules:

- Does not depend on any other layer
- Does not use frameworks
- 100% business-focused

---

### 5. Application Layer

> Orchestrates system use cases.

#### Contains:

- **Use Cases** → Application services
- **DTOs** → Input/output structures

#### Responsibilities:

- Coordinate domain entities and services
- **Manage transaction boundaries through the Unit of Work port**
- Emit events
- Apply application rules (not business rules)

#### Example:

```
ConfirmOrderUseCase
CancelOrderUseCase
ReserveStockUseCase
```

#### Transaction pattern:

```python
async with self.unit_of_work as uow:
    # All reads and writes share the same session/transaction
    entity = await uow.repository.find(...)
    entity.do_something()
    await uow.repository.save(entity)
    await uow.commit()
```

---

### 6. Infrastructure Layer

> Technical implementations of domain-defined contracts.

#### Contains:

- **ORM Models**
- **Repository Implementations**
- **Unit of Work Adapters** → Concrete transaction managers
- **External Services (APIs, queues, email, etc.)**
- **Mappers (Domain ↔ Persistence)**

#### Example:

```
SQLAlchemyUserUnitOfWorkAdapter
SQLAlchemyOrderRepository
CeleryNotificationService
Postgres models
```

#### Key rule:

- Depends on `domain` (implements its interfaces)
- Never contains business logic
- The Unit of Work adapter owns the session lifecycle

---

### 7. Presentation Layer

> System entry point (HTTP / API)

#### Contains:

- **Routes (FastAPI)**
- **Schemas (Pydantic)**
- **Mappers (Request ↔ DTO)**
- **Exception Handlers**
- **Dependency Injection (compositions)**

#### Responsibilities:

- Validate input
- Transform request → DTO
- Call use cases
- Transform response → HTTP

---

## 8. Detailed Example — Orders Module

```
orders/
├── application/
│   ├── dtos/
│   └── use_cases/
│
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── events/
│   ├── exceptions/
│   └── ports/
│       ├── repositories/
│       ├── unit_of_work/
│       └── outbound/
│
├── infrastructure/
│   ├── persistence/
│   │   ├── models/
│   │   ├── mappers/
│   │   ├── repositories/
│   │   └── unit_of_work/
│   └── outbound/
│
└── presentation/
    └── api/
        ├── routes/
        ├── schemas/
        ├── mappers/
        ├── exceptions/
        └── compositions/
```

---

## 9. Unit of Work Pattern

### Purpose

The Unit of Work (UoW) pattern centralises transaction control at the **application layer**. A use case opens exactly one UoW, performs all repository interactions through it, and either commits or lets it roll back — guaranteeing atomicity without leaking session management into domain or presentation code.

### Port hierarchy

```
shared/domain/ports/unit_of_work/unit_of_work_port.py    ← base ABC
    └── modules/<name>/domain/ports/unit_of_work/<name>_unit_of_work_port.py
            └── exposes module-specific repositories
```

### Adapter location

```
modules/<name>/infrastructure/persistence/unit_of_work/
    sqlalchemy_<name>_unit_of_work_adapter.py
```

### Lifecycle

```
async with unit_of_work as uow:   # __aenter__: new session created, repos initialised
    ...                            # business operations via uow.repo
    await uow.commit()             # flush + commit
                                   # __aexit__: session closed
                                   # on exception → auto rollback + session closed
```

### Rules

1. **One UoW per use case execution** — never share a UoW across use cases.
2. **Domain validation runs before opening the UoW** — Value Object construction raises domain exceptions eagerly, so no session is opened for invalid input.
3. **No session references leak outside the UoW** — repositories are only accessible inside the `async with` block.
4. **Commit is explicit** — callers must call `await uow.commit()`. The UoW never auto-commits on clean exit.
5. **Rollback is automatic on unhandled exception** — `__aexit__` rolls back if `exc_type is not None`.

### Auth module example

```
UserUnitOfWorkPort (domain/ports/unit_of_work)
    .users: UserRepositoryPort

SQLAlchemyUserUnitOfWorkAdapter (infrastructure/persistence/unit_of_work)
    session_factory → AsyncSession
    .users → SQLAlchemyUserRepositoryAdapter(session)
```

---

## 10. Dependency Flow

Dependencies always flow **inward**:

```
presentation → application → domain
                    ↓
             infrastructure
```

### Import Rules

- `domain` → imports nothing
- `application` → imports domain
- `infrastructure` → imports domain
- `presentation` → imports application

---

## 11. Shared Module

```
shared/
 ├── domain/
 ├── application/
 ├── infrastructure/
 └── presentation/
```

### Contains:

- Common utilities
- Base classes
- Cross-cutting concerns:

  - Logging
  - Database configuration
  - Event bus
  - Base exceptions
  - Base Unit of Work port

### Rule:

- Must not contain domain-specific business logic

---

## 12. Module Communication

Modules are **not directly coupled**.

### Communication methods:

#### 1. Via Application Layer

- One module uses another module's use case

#### 2. Via Domain Events

- Example:

  - `OrderConfirmed` → triggers notification

#### 3. Via Ports (Interfaces)

- Domain defines contracts
- Infrastructure implements them

---

## 13. Request Flow (End-to-End)

1. HTTP request reaches **FastAPI (presentation)**
2. Validation via **Pydantic schema**
3. Mapper → DTO
4. **Use Case** is executed
5. Use Case opens a **Unit of Work**:

   - Interacts with repositories through `uow.<repo>`
   - Calls `await uow.commit()` on success
6. Infrastructure implements the UoW adapter and its repositories
7. Persistence / external logic execution
8. Response → Presentation → HTTP

---

## 14. Key Benefits

### 1. Maintainability

- Infrastructure changes do not affect the domain

### 2. Testability

- Domain and Application are easily testable (no DB required)
- Unit tests mock the entire UoW with a simple `MagicMock`
- Integration tests verify the UoW adapter's commit/rollback guarantees

### 3. Scalability

- Each module can evolve independently

### 4. Atomic transactions

- All writes within a use case are committed or rolled back together

### 5. Flexibility

You can change:

- Database
- Framework
- Messaging system

without breaking the core

---

## 15. Architectural Decisions

- Modular Monolith (no microservices initially)
- Domain-centric design
- Explicit module boundaries
- Ports & Adapters for infrastructure decoupling
- **Unit of Work for transaction boundary management**

---

## 16. When to Extract Microservices

The system can evolve into microservices when:

- A module has independent high load
- It needs to scale separately
- It has a clear bounded context (e.g., orders)

---

## 17. Summary

Silver Enigma implements an architecture that is:

- **Modular**
- **Domain-driven**
- **Decoupled**
- **Scalable-ready**
- **Transactionally safe via Unit of Work**

Where:

- The **domain drives everything**
- The **infrastructure is replaceable**
- The **modules are autonomous**
- The **application layer owns transaction boundaries**
