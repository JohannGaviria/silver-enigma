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
9. [Key Benefits](#13-key-benefits)
10. [Architectural Decisions](#14-architectural-decisions)
11. [When to Extract Microservices](#15-when-to-extract-microservices)
12. [Summary](#16-summary)

---

## 1. Overview

**Silver Enigma** is designed using:

- **Domain-Driven Design (DDD)**
- **Clean Architecture (Ports & Adapters)**
- **Modular Monolith (domain-based)**

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
- Handle transactions (via repositories)
- Emit events
- Apply application rules (not business rules)

#### Example:

```
ConfirmOrderUseCase
CancelOrderUseCase
ReserveStockUseCase
```

---

### 6. Infrastructure Layer

> Technical implementations of domain-defined contracts.

#### Contains:

- **ORM Models**
- **Repository Implementations**
- **External Services (APIs, queues, email, etc.)**
- **Mappers (Domain ↔ Persistence)**

#### Example:

```
SQLAlchemyOrderRepository
CeleryNotificationService
Postgres models
```

#### Key rule:

- Depends on `domain` (implements its interfaces)
- Never contains business logic

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
│       └── outbound/
│
├── infrastructure/
│   ├── persistence/
│   │   ├── models/
│   │   ├── mappers/
│   │   └── repositories/
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

## 9. Dependency Flow

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

## 10. Shared Module

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

### Rule:

- Must not contain domain-specific business logic

---

## 11. Module Communication

Modules are **not directly coupled**.

### Communication methods:

#### 1. Via Application Layer

- One module uses another module’s use case

#### 2. Via Domain Events

- Example:

  - `OrderConfirmed` → triggers notification

#### 3. Via Ports (Interfaces)

- Domain defines contracts
- Infrastructure implements them

---

## 12. Request Flow (End-to-End)

1. HTTP request reaches **FastAPI (presentation)**
2. Validation via **Pydantic schema**
3. Mapper → DTO
4. **Use Case** is executed
5. Use Case interacts with:

   - Entities
   - Domain Services
   - Repositories (ports)
6. Infrastructure implements repositories
7. Persistence / external logic execution
8. Response → Presentation → HTTP

---

## 13. Key Benefits

### 1. Maintainability

- Infrastructure changes do not affect the domain

### 2. Testability

- Domain and Application are easily testable (no DB required)

### 3. Scalability

- Each module can evolve independently

### 4. Flexibility

You can change:

- Database
- Framework
- Messaging system

without breaking the core

---

## 14. Architectural Decisions

- Modular Monolith (no microservices initially)
- Domain-centric design
- Explicit module boundaries
- Ports & Adapters for infrastructure decoupling

---

## 15. When to Extract Microservices

The system can evolve into microservices when:

- A module has independent high load
- It needs to scale separately
- It has a clear bounded context (e.g., orders)

---

## 16. Summary

Silver Enigma implements an architecture that is:

- **Modular**
- **Domain-driven**
- **Decoupled**
- **Scalable-ready**

Where:

- The **domain drives everything**
- The **infrastructure is replaceable**
- The **modules are autonomous**
