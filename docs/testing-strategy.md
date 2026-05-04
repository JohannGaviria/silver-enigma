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
8. [Test Naming Convention](#8-test-naming-convention)
9. [Summary](#summary)

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

## 8. Test Naming Convention

A consistent naming convention improves readability, intent clarity, and maintainability of tests.

### General Pattern

All test methods should follow:

```text
test_should_<expected_behavior>_when_<condition>
```

### Examples

```python
def test_should_create_user_when_data_is_valid() -> None:
  ...

def test_should_raise_exception_when_email_is_invalid() -> None:
  ...

def test_should_return_empty_list_when_no_orders_exist() -> None:
  ...
```

### Naming Rules

#### 1. Start with `test_`

Required by pytest for automatic discovery.

#### 2. Use `should`

Encourages behavior-driven thinking and makes intent explicit.

#### 3. Describe the **expected outcome first**

Focus on **what the system should do**, not how.

Correct:

```python
test_should_return_user_when_id_exists
```

Avoid:

```python
test_get_user_by_id
```

#### 4. Use `when` for context (optional but recommended)

Clarifies the scenario under which the behavior happens.

```python
test_should_fail_when_password_is_incorrect
```

#### 5. Keep names concise but expressive

Bad:

```python
test_should_return_error_when_user_tries_to_login_with_wrong_password_and_email_is_not_verified_and_account_is_blocked
```

Better:

```python
test_should_fail_login_when_password_is_incorrect
```

Split into multiple tests if needed.

### Class Naming

Test classes must have the **same name as the class under test**, prefixed with `Test`.

```python
class TestUserEntity:
  ...

class TestEmailVO:
  ...

class TestCreateOrderUseCase:
  ...
```

### File Naming

Test files must have the **exact same name as the file under test**, prefixed with `test_`.

```
test_<original_filename>.py
```

### Examples

If the source files are:

```text
user_entity.py
email_vo.py
create_order_use_case.py
```

Then the test files must be:

```text
test_user_entity.py
test_email_vo.py
test_create_order_use_case.py
```

And inside each file, the test class must match the main unit:

```python
# test_user_entity.py
class TestUserEntity:
    ...
```

### Additional Guidelines

* Avoid generic names like `test_1`, `test_example`
* Each test should validate **one behavior**
* Prefer clarity over brevity
* Names should be understandable without reading the implementation

---

## 9. Summary

| Type        | Layer          | Focus             | Speed  | Dependencies |
| ----------- | -------------- | ----------------- | ------ | ------------ |
| Unit        | Domain / App   | Business logic    | Fast   | Mocked       |
| Integration | Infrastructure | DB, ORM, adapters | Medium | Real         |
| E2E         | Presentation   | Full HTTP flow    | Slow   | Real         |
