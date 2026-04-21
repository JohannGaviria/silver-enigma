# DevOps Documentation — Silver Enigma

## Table of Contents

1. [Overview](#1-overview)
2. [Environments](#2-environments)
3. [Containerization](#3-containerization)

   * [Dockerfile](#dockerfile)
   * [Docker Compose](#docker-compose)
4. [CI — Continuous Integration](#4-ci--continuous-integration)

   * [Trigger](#trigger)
   * [Objective](#objective)
   * [Stages](#stages)
5. [CD — Continuous Deployment](#5-cd--continuous-deployment)

   * [Trigger](#trigger-1)
   * [Objective](#objective-1)
   * [Deployment Strategies](#deployment-strategies)
6. [Versioning Strategy](#6-versioning-strategy)
7. [Secrets Management](#7-secrets-management)
8. [Deployment Flow](#8-deployment-flow)
9. [Local Development Workflow](#9-local-development-workflow)
10. [Best Practices](#10-best-practices)

---

## 1. Overview

The project’s DevOps approach is designed to ensure:

* Fast and safe deliveries
* High reliability in deployments
* Environment reproducibility
* Full automation of the software lifecycle

It is based on:

* Containers (Docker)
* Local orchestration (docker-compose)
* Separate CI and CD pipelines
* Integration with a Git repository

---

## 2. Environments

The following environments are defined:

| Environment | Purpose                           |
| ----------- | --------------------------------- |
| Development | Local development with hot reload |
| Testing     | Automated test execution          |
| Production  | Live production environment       |

---

## 3. Containerization

### Dockerfile

The main service is containerized using Docker, enabling:

* Consistency across environments
* Portability
* Dependency isolation

**Dockerfile responsibilities:**

* Define base image
* Install dependencies
* Copy source code
* Define entrypoint

---

### Docker Compose

The `docker-compose.yml` file allows spinning up the full environment.

**Services:**

* API (FastAPI) — backend
* Database (PostgreSQL) — postgres
* Redis (queues/cache) — redis
* Workers (Celery) — workers

**Benefits:**

* Reproducible environment
* Local production-like simulation
* Easy onboarding

---

## 4. CI — Continuous Integration

Pipeline defined in: `ci.yml`

### Trigger

* Push to branches: `develop`, `main`
* Pull Requests

### Objective

Validate code quality before integration.

### Stages

#### 1. Checkout

Clones the repository.

#### 2. Setup Environment

* Install dependencies
* Configure runtime (Python, etc.)

#### 3. Linting

* Style validation (PEP8, flake8, etc.)

#### 4. Testing

* Unit Tests → Domain & Application
* Integration Tests → Infrastructure

### CI Result

The pipeline fails if:

* There are linting errors
* Tests fail

This prevents unstable code from reaching main branches.

---

## 5. CD — Continuous Deployment

Pipeline defined in: `cd.yml`

### Trigger

* Push to `main`
* Release tags

### Objective

Automate deployment to production or staging.

### Stages

#### 1. Build Docker Image

* Build final image
* Tagging (latest + version)

#### 2. Push to Registry

* Docker Hub / Container Registry

#### 3. Deploy

Depending on infrastructure:

* SSH to server
* Kubernetes apply
* Docker Compose pull & up

### Deployment Strategies

* Rolling updates
* Image versioning

---

## 6. Versioning Strategy

Semantic versioning is used:

```
MAJOR.MINOR.PATCH
```

Example:

* `1.0.0` → initial release
* `1.1.0` → new features
* `1.1.1` → bug fix

---

## 7. Secrets Management

Credentials are not stored in the codebase.

They are managed via:

* Environment variables
* GitHub Secrets (CI/CD)
* `.env` files (local)

---

## 8. Deployment Flow

Full flow:

1. Developer pushes code
2. CI pipeline runs:

   * Lint
   * Tests
3. If successful:

   * Merge to `main`
4. CD pipeline:

   * Build image
   * Push to registry
   * Automatic deploy

---

## 9. Local Development Workflow

```bash
# Build containers
docker compose build

# Run services
docker compose up

# Stop
docker compose down
```

---

## 10. Best Practices

* Keep CI fast (< 5 minutes ideally)
* Avoid business logic in pipelines (only orchestration)
* Use lightweight images (alpine/slim)
* Do not couple infrastructure to the application
* Always validate before deployment (CI is mandatory)
