# Testing Strategy — Silver Enigma

> Defines what is tested, how it is tested, and why—ensuring quality, reliability, and safe system evolution.

---

## Table of Contents

1. [Objective](#objective)
2. [Testing Pyramid](#testing-pyramid)
3. [Unit Testing](#1-unit-testing)
4. [Integration Testing](#2-integration-testing)
5. [End-to-End Testing (E2E)](#3-end-to-end-testing-e2e)
6. [Key Principles](#4-key-principles)
7. [Specifications](#5-specifications)
8. [Summary](#summary)

---

## 1. Objective

Ensure the system is:

* **Correct** → Business logic behaves as expected
* **Reliable** → Changes do not break existing functionality
* **Maintainable** → Safe refactoring
* **Predictable** → Behavior is verifiable end-to-end

---

## 2. Testing Pyramid

The strategy follows a classic pyramid:

```
        E2E (Few)
    Integration (Some)
  Unit Tests (Many)
```

---

## 3. Unit Testing

### What is tested

* **Domain Layer**

  * Entities
  * Value Objects
  * Domain Services
  * Business rules

* **Application Layer**

  * Use Cases
  * Logic orchestration
  * Flow validations

### How it is tested

* No external dependencies (DB, APIs, Redis, etc.)
* Use of mocks/stubs for:

  * Repositories (interfaces)
  * External services
* Fast and deterministic tests

### Why

* Detects business logic errors early
* Enables safe refactoring
* Fastest and cheapest layer to maintain

---

## 4. Integration Testing

### What is tested

The **Infrastructure Layer** and its integration:

* Real repositories (PostgreSQL)
* ORM (SQLAlchemy)
* Redis (if applicable)
* Celery (sync or test mode)
* External adapters

### How it is tested

* Real database (test DB)
* Transaction rollback per test
* Controlled fixtures
* No infrastructure mocks

### Why

* Validates infrastructure correctness
* Detects configuration issues (ORM, connections, queries)
* Ensures contracts between layers are respected

---

## 5. End-to-End Testing (E2E)

### What is tested

Full flow from the **Presentation Layer**:

* HTTP API (FastAPI)
* Routing
* Validation (Pydantic)
* Use Cases
* Persistence
* Final response

### How it is tested

* Real HTTP requests (TestClient / httpx)
* Running system (or partially simulated)
* Real or isolated database
* No mocks (or minimal)

### Why

* Ensures the entire system works together
* Detects wiring issues (DI, routers, middleware)
* Validates external contracts (API)

---

## 6. Key Principles

### 1. Test behavior, not implementation

Incorrect:

```python
assert repository._session is not None
```

Correct:

```python
assert order.status == "confirmed"
```

### 2. Independent tests

* Tests must not depend on each other
* Each test sets up its own state

### 3. Determinism

* Same inputs → same outputs
* Avoid uncontrolled randomness

### 4. Speed matters

* Unit tests → very fast
* Integration → moderate
* E2E → slower, but fewer

---

## 7. Specifications

### What is NOT directly tested

* Frameworks (FastAPI, SQLAlchemy)
* External libraries
* Trivial code without logic

### Expected Coverage

* **High in Domain Layer (~90–100%)**
* **Medium in Application Layer (~80–90%)**
* **Selective in Integration**
* **Critical in E2E (main flows)**

### CI Strategy

* Unit tests → run on every commit
* Integration tests → run on PR
* E2E tests → run on PR or pre-release

---

## 8. Summary

| Type        | Layer          | Focus             | Speed  | Dependencies |
| ----------- | -------------- | ----------------- | ------ | ------------ |
| Unit        | Domain / App   | Business logic    | Fast   | Mocked       |
| Integration | Infrastructure | DB, ORM, adapters | Medium | Real         |
| E2E         | Presentation   | Full HTTP flow    | Slow   | Real         |
