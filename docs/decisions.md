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

- **No atomic multi-repository writes**: if a use case interacted with two or more repositories, there was no guarantee that all changes would be committed together or not at all.
- **Session lifecycle ambiguity**: the session was created outside the use case, but committed inside a repository — making ownership unclear and rollback difficult.
- **Poor unit testability**: mocking individual repositories worked, but there was no single seam to verify that the whole interaction (read → write → commit) happened atomically.

### Considered alternatives

- **Keep per-repository commits**: simple, but fundamentally unsafe for multi-step operations.
- **Pass the session to the use case**: use case would call `session.commit()` directly — couples the application layer to SQLAlchemy.
- **Middleware / dependency-injection-level transaction**: a FastAPI dependency opens and closes the session around each request — hard to test and forces one transaction per HTTP request regardless of use-case needs.
- **Unit of Work pattern**: application layer depends only on abstract Unit of Work ports; infrastructure provides SQLAlchemy implementations.

### Decision: Unit of Work port per transactional business capability

Each module may define one or more Unit of Work ports depending on the transactional needs of the domain.

A Unit of Work groups the repositories required to execute a business operation atomically within a single transaction.

Simple modules may expose entity-oriented Unit of Work ports such as:

- `UserUnitOfWorkPort`
- `ProductUnitOfWorkPort`
- `WarehouseUnitOfWorkPort`

As the domain evolves, more complex operations may require capability-oriented Unit of Work ports that coordinate multiple repositories within the same transaction.

Example:

- `InventoryUnitOfWorkPort`

which may coordinate:

- `ProductRepositoryPort`
- `WarehouseRepositoryPort`
- `StockRepositoryPort`

The goal of a Unit of Work is not to represent a single entity, but to guarantee transactional consistency for a business operation.

The infrastructure layer provides a corresponding SQLAlchemy adapter for each Unit of Work port.

Each adapter:

1. Creates a fresh `AsyncSession` on `__aenter__`.
2. Binds all required repositories to that single session.
3. Rolls back automatically on unhandled exceptions in `__aexit__`.
4. Exposes explicit `commit()` and `rollback()` methods for the use case to call.

### Key design choices

- **Domain validation before the UoW opens**: Value Objects are constructed (and validated) before `async with unit_of_work`. Invalid input never opens a session.
- **Explicit commit**: the UoW never auto-commits on clean exit. The use case must call `await uow.commit()` — making the intent visible in code.
- **One session per use case execution**: the session factory creates a new session on every `__aenter__`, guaranteeing isolation between concurrent requests.
- **Unit tests mock the entire UoW**: a `MagicMock` configured as an async context manager replaces the real adapter — no database required for use-case tests.
- **Integration tests validate the adapter contract**: `commit`, `rollback`, auto-rollback on exception, and session isolation are all tested against a real PostgreSQL instance.
- **Repositories participating in the same business transaction must share the same UoW**: coordinating multiple independent UoWs in a single use case is forbidden because it breaks transactional guarantees.

### Naming convention

| Artifact | Location | Example |
|-----------|-----------|-----------|
| Base UoW port | `shared/domain/ports/unit_of_work/unit_of_work_port.py` | `UnitOfWorkPort` |
| Entity-oriented UoW port | `<module>/domain/ports/unit_of_work/*.py` | `UserUnitOfWorkPort` |
| Capability-oriented UoW port | `<module>/domain/ports/unit_of_work/*.py` | `InventoryUnitOfWorkPort` |
| UoW adapter | `<module>/infrastructure/persistence/unit_of_work/*.py` | `SQLAlchemyUserUnitOfWorkAdapter` |

### Trade-off

Additional indirection (ports, adapters, and UoW implementations).

Justified because:

- Use cases remain framework-agnostic and trivially testable.
- Transaction atomicity is guaranteed by design, not by convention.
- Multiple repositories can participate safely in the same transaction.
- Business capabilities can evolve without forcing repository-specific transaction boundaries.
- The pattern scales cleanly as the domain grows and cross-aggregate operations become more common.

---

## ADR-009: Cross-module communication through consumer-owned ports

### Context

As the domain evolved, business rules began requiring information owned by other modules.

Examples:

- Inventory operations must verify whether a warehouse exists and belongs to the supplier performing the action.
- Products must verify whether active orders exist before allowing deactivation or price changes.
- Warehouses must verify whether active orders exist before allowing deactivation.

The project follows a modular monolith architecture where modules should remain as independent as possible and only depend on shared technical abstractions.

A naive implementation would allow modules to import repositories, entities, or services from other modules directly:

```text
Products
    ↓
Warehouses

---

## ADR-009: Cross-module communication through consumer-owned ports

### Context

As the domain evolved, some business rules required information owned by other modules.

Examples:

- Inventory operations need to verify whether a warehouse exists and belongs to the supplier performing the action.
- Products must verify whether active orders exist before allowing deactivation.
- Products must verify whether active orders exist before allowing price changes.
- Warehouses must verify whether active orders exist before allowing deactivation.

The project follows a modular monolith architecture where modules should remain as independent as possible and only depend on shared abstractions.

A naive implementation would allow modules to import repositories, entities, or services from other modules directly:

```text
Products
    ↓
Warehouses
```

or

```text
Warehouses
    ↓
Orders
```

This creates tight coupling between modules, increases maintenance costs, and makes future extraction into independent services more difficult.

### Considered alternatives

#### Direct repository imports

Allow a module to use repositories from another module directly.

##### Pros

- Simple implementation.
- Minimal upfront code.

##### Cons

- Strong compile-time coupling between modules.
- Increased risk of cyclic dependencies.
- Business boundaries become progressively blurred.

#### Shared cross-module ports

Define all cross-module contracts inside the Shared layer.

##### Pros

- Avoids direct module-to-module imports.
- Contracts are centralized.

##### Cons

- Pollutes the Shared layer with domain-specific concepts.
- Shared becomes a dumping ground for business concerns.
- Weakens bounded-context boundaries.

#### Domain events and local projections

Publish domain events and maintain local read models inside consuming modules.

##### Pros

- Maximum decoupling.
- Suitable for distributed systems and microservices.

##### Cons

- Introduces eventual consistency.
- Significantly increases complexity.
- Unnecessary for the current scale and requirements of the project.

#### Consumer-owned ports

The consuming module defines the contract it needs, while the provider module implements it.

### Decision: Consumer-owned ports

When a module requires information owned by another module, it must define a dedicated port that represents its business need.

The provider module supplies an implementation of that port through dependency injection.

Example:

```text
products/
└── application/
    └── ports/
        └── warehouse_query_port.py
```

```python
class WarehouseQueryPort(ABC):

    @abstractmethod
    async def exists_warehouse(
        self,
        warehouse_id: UUID,
    ) -> bool:
        ...

    @abstractmethod
    async def belongs_to_supplier(
        self,
        warehouse_id: UUID,
        supplier_id: UUID,
    ) -> bool:
        ...
```

The Warehouses module provides the implementation:

```text
warehouses/
└── infrastructure/
    └── services/
        └── warehouse_query_service.py
```

Dependency injection is responsible for wiring both components together.

### Ownership rule

A port always belongs to the module that needs the information, not the module that owns the data.

Examples:

| Consumer   | Provider   | Port Location                                                          |
|------------|------------|------------------------------------------------------------------------|
| Products   | Warehouses | `products/domain/ports/repositories/warehouse_query_port.py`           |
| Products   | Orders     | `products/domain/ports/repositories//ports/order_validation_port.py`   |
| Warehouses | Orders     | `warehouses/domain/ports/repositories//ports/order_validation_port.py` |

This keeps dependencies pointing toward abstractions rather than implementations.

### Why not Shared

The Shared layer exists to host generic technical abstractions such as:

- Base entities
- Base value objects
- Repository abstractions
- Unit of Work abstractions
- Shared exceptions
- Common utilities

Business-specific concepts such as:

- Warehouse queries
- Order validations
- Product availability checks

must remain within the modules that require them.

Otherwise, Shared gradually becomes a central repository for domain logic, violating bounded-context separation.

### Design principles

- Modules never import repositories from other modules.
- Modules never import entities from other modules.
- Cross-module communication happens through ports.
- Ports expose only the information required by the consuming use case.
- Ports should model business questions, not persistence operations.
- Implementations remain inside the provider module.

### Benefits

- Preserves module independence.
- Maintains clear dependency direction.
- Prevents architectural erosion over time.
- Reduces the likelihood of cyclic dependencies.
- Makes business requirements explicit through contracts.
- Facilitates future migration to independent services if required.

### Trade-off

Cross-module interactions require additional ports and adapters.

This introduces extra boilerplate, but the explicit contracts and clear module boundaries outweigh the added complexity as the system grows.

---

## ADR-010: Persisted inventory movement audit trail

### Context

One of the non-functional requirements of the inventory module establishes that every stock movement must be auditable.

The original requirement stated:

> Every stock movement must emit a log containing:
>
> - product identifier
> - warehouse identifier
> - affected quantity
> - movement type (`RESERVE`, `RELEASE`, `DECREMENT`)
> - originating order

Applicable requirements:

- US-RF-012
- US-RF-016
- US-RF-018
- US-RF-020
- US-RF-021

The requirement did not explicitly define how this information should be stored.

Initially, the term *log* could be interpreted as application-level logging through the standard logging infrastructure (`logger.info`, structured logs, ELK, etc.).

However, inventory movements are business-critical events whose history must remain available for:

- Operational auditing
- Investigation of stock inconsistencies
- Traceability of inventory changes
- Production incident analysis
- Historical reconstruction of inventory behavior

Application logs are not designed to provide these guarantees because they may be:

- Rotated
- Deleted
- Aggregated externally
- Filtered
- Unavailable after infrastructure changes

As a result, relying solely on application logging would not satisfy the long-term auditability requirements of the inventory domain.

### Considered alternatives

#### Application logs only

Store movement information exclusively through the logging system.

##### Pros

- Simple implementation
- No additional database tables
- Low development effort

##### Cons

- Audit history depends on log retention policies
- Difficult to query from business workflows
- No referential integrity
- Historical data may be lost
- Does not model inventory movements as domain concepts

#### Domain events only

Emit inventory movement events without persisting them directly.

##### Pros

- Decoupled architecture
- Facilitates future integrations

##### Cons

- Requires additional infrastructure
- Historical reconstruction depends on event retention
- Adds complexity without immediate business benefit

#### Persisted inventory movement records

Store every inventory movement as a database record.

##### Pros

- Full audit trail
- Queryable historical information
- Referential integrity with domain entities
- Simplifies debugging and operational support
- Explicitly models inventory movement as part of the domain

##### Cons

- Additional storage consumption
- Extra write operation per stock movement

### Decision: Persist inventory movements as a domain entity

Inventory movements are modeled as a first-class domain concept and persisted in the database.

A new entity is introduced:

```text
InventoryMovement
```

Every successful stock operation must create a corresponding movement record within the same transaction.

Supported movement types:

```text
RESERVE
RELEASE
DECREMENT
```

Persisted structure:

```sql
inventory_movement
(
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    warehouse_id UUID NOT NULL,
    order_id UUID NOT NULL,
    movement_type inventory_movement_type NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL
)
```

Relationships:

```text
inventory_movement.product_id   -> products.id
inventory_movement.warehouse_id -> warehouses.id
inventory_movement.order_id     -> orders.id
```

### Transactional guarantee

The inventory movement record must be persisted within the same transaction that modifies stock.

This guarantees:

```text
Stock updated
        +
Movement recorded
```

or

```text
Neither operation is committed
```

Partial success is not allowed.

### Domain implications

This decision extends the Inventory bounded context with a new aggregate/entity responsible for representing historical stock changes.

Inventory movements are not merely technical logs.

They represent business events that occurred in the system and therefore belong to the domain model.

### Benefits

- Complete auditability of stock operations.
- Historical traceability of inventory changes.
- Easier debugging of production incidents.
- Referential integrity with products, warehouses, and orders.
- Enables future reporting and analytics features without relying on external logging systems.
- Preserves inventory history independently of infrastructure log retention policies.

### Trade-off

Each inventory operation generates an additional database write.

This overhead is accepted because auditability and traceability are considered more important than the small storage and write-performance cost introduced by the solution.

---

# ADR-011: Rename inventory stock terminology for domain clarity

## Context

The inventory model currently uses the following terminology:

```text
total_stock
available_stock
stock_disponible
```

However, analysis of the inventory and order lifecycle revealed that `available_stock` does not represent stock available for purchase.

According to the business rules:

- Order confirmation increases `available_stock`.
- Order cancellation decreases `available_stock`.
- Order shipment decreases both `total_stock` and `available_stock`.

This behavior indicates that `available_stock` actually represents stock already committed to active orders.

The current naming introduces ambiguity because developers naturally interpret:

```text
available_stock
```

as inventory that can still be sold.

The model therefore requires constant mental translation between the name and its actual business meaning.

## Considered alternatives

### Keep current terminology

Maintain:

```text
total_stock
available_stock
stock_disponible
```

#### Pros

- No refactoring required.
- No API or database changes.

#### Cons

- Business meaning remains unclear.
- Higher risk of implementation mistakes.
- Requires developers to learn a non-intuitive interpretation.
- Contradicts common inventory terminology.

### Rename only internal domain objects

Keep external contracts unchanged while renaming domain concepts.

#### Pros

- Improves internal readability.
- Avoids API breaking changes.

#### Cons

- Two different vocabularies coexist.
- Mapping complexity increases.
- Documentation remains inconsistent.

### Adopt domain-accurate terminology everywhere

Rename inventory concepts to match their actual business meaning.

#### Pros

- Consistent ubiquitous language.
- Clearer business intent.
- Easier maintenance.
- Reduced cognitive load.

#### Cons

- Requires refactoring.
- May require database migrations and API adjustments.

## Decision: Adopt domain-accurate stock terminology

The inventory model will use the following terminology:

| Previous Name      | New Name          |
| ------------------ | ----------------- |
| `total_stock`      | `total_stock`     |
| `available_stock`  | `reserved_stock`  |
| `stock_disponible` | `available_stock` |

Conceptually:

```text
total_stock
    = physical inventory

reserved_stock
    = inventory committed to active orders

available_stock
    = total_stock - reserved_stock
```

## Business interpretation

Example:

```text
total_stock     = 100
reserved_stock  = 30
available_stock = 70
```

Meaning:

- 100 physical units exist in the warehouse.
- 30 units are already reserved by confirmed orders.
- 70 units remain available for new purchases.

Order lifecycle operations become explicit:

```text
CONFIRMED
    reserved_stock += quantity

CANCELLED
    reserved_stock -= quantity

SHIPPED
    total_stock -= quantity
    reserved_stock -= quantity
```

## Design principles

- Entity attributes should describe their actual business meaning.
- Derived values should be named according to what they represent, not how they are calculated.
- Inventory terminology must be understandable without requiring knowledge of implementation details.
- Domain language should align with common inventory-management concepts.

## Benefits

- Eliminates ambiguity in the inventory model.
- Improves readability of business rules.
- Reduces the likelihood of stock-related bugs.
- Makes order lifecycle operations easier to understand.
- Establishes a clearer ubiquitous language across Inventory and Orders modules.

## Trade-off

Existing code, tests, documentation, DTOs, and persistence mappings may require refactoring.

This cost is considered acceptable because the improvement affects a core business concept used throughout the system and prevents long-term confusion in future development.

---

# ADR-012: Order lifecycle tracking through status history

## Context

The initial order model stored lifecycle timestamps directly inside the `orders` table:

```sql
orders
(
    id UUID,
    status order_status,
    confirmed_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP
)
```

This approach creates duplicated state information.

The current status:

```text
orders.status
```

and lifecycle timestamps:

```text
confirmed_at
shipped_at
delivered_at
cancelled_at
```

represent the same domain concept from different perspectives.

As the order lifecycle evolves, this model becomes difficult to maintain because every new status or transition requires adding another column.

Examples:

Future states:

```text
RETURN_REQUESTED
RETURNED
PAYMENT_FAILED
ON_HOLD
```

would require additional fields:

```text
returned_at
payment_failed_at
on_hold_at
```

The order entity would progressively accumulate lifecycle-specific columns.

Additionally, timestamps alone do not provide enough audit information:

- Who changed the order state?
- What was the previous state?
- Was the change manual or automatic?
- How many transitions occurred?

For B2B operations, order lifecycle traceability is a business requirement.

---

## Considered alternatives

### Store lifecycle timestamps in orders

Keep columns such as:

```sql
confirmed_at
shipped_at
delivered_at
cancelled_at
```

#### Pros

- Simple queries.
- Fast access to common timestamps.
- Minimal implementation complexity.

#### Cons

- Schema changes required for every new status.
- Duplicates information already represented by status transitions.
- Cannot track who performed the change.
- Cannot represent repeated transitions.
- Weak audit capability.

---

### Create a generic order dates table

Store status timestamps separately:

```sql
order_dates
(
    order_id,
    status,
    timestamp
)
```

#### Pros

- Removes lifecycle columns from orders.
- Supports additional statuses.

#### Cons

- Represents only timestamps, not transitions.
- Does not capture previous status.
- Does not capture the actor responsible.
- Duplicates the purpose of a status history table.

---

### Persist order status history

Store every state transition as an immutable record.

Example:

```sql
order_status_history
(
    id UUID,
    order_id UUID,
    previous_status order_status,
    new_status order_status,
    changed_by UUID,
    changed_by_role user_role,
    changed_at TIMESTAMP
)
```

#### Pros

- Complete lifecycle audit trail.
- Supports unlimited future statuses.
- Captures transition context.
- Allows reconstruction of order history.
- Matches B2B traceability requirements.

#### Cons

- Requires an additional query to retrieve historical timestamps.
- Slightly more storage usage.

## Decision: Use order_status_history as the source of lifecycle history

The `orders` table will store only the current state:

```sql
orders
(
    id UUID,
    buyer_id UUID,
    supplier_id UUID,
    warehouse_id UUID,
    status order_status,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

Lifecycle transitions will be persisted in:

```sql
order_status_history
(
    id UUID,
    order_id UUID,

    previous_status order_status,
    new_status order_status,

    changed_by UUID,
    changed_by_role user_role,

    changed_at TIMESTAMP,
    created_at TIMESTAMP
)
```

Every status transition must create a history record within the same database transaction that updates the order status.

The invariant is:

```text
Order status updated
        +
Status transition recorded
```

or:

```text
Neither operation is committed
```

Partial persistence is not allowed.

## Domain rules

The current state is optimized for operational queries:

```text
orders.status = CONFIRMED
```

The history is optimized for auditing:

```text
How did this order reach CONFIRMED?
```

Examples:

Retrieve confirmation date:

```text
First transition where:

new_status = CONFIRMED
```

Retrieve shipment date:

```text
First transition where:

new_status = SHIPPED
```

Retrieve cancellation history:

```text
All transitions where:

new_status = CANCELLED
```

## Design principles

- The current state belongs to the aggregate root.
- Historical transitions belong to an immutable audit trail.
- Do not duplicate derived lifecycle information.
- Schema design should support future domain evolution.
- Business-critical state changes must be traceable.

## Benefits

- Removes duplicated lifecycle data.
- Supports unlimited order states without schema changes.
- Provides complete order traceability.
- Enables operational debugging and compliance auditing.
- Keeps the `orders` table focused on current aggregate state.

## Trade-off

Reading lifecycle timestamps requires querying `order_status_history` instead of reading a column directly from `orders`.

This additional query complexity is accepted because order traceability and future extensibility are more important than optimizing access to individual timestamps.

---

# ADR-013: Warehouse assignment happens during fulfillment, not order creation

## Context

The initial order creation flow considered storing `warehouse_id` directly in the `orders` table.

The reasoning behind this approach was that every order would eventually be fulfilled from a warehouse, so associating an order with a warehouse appeared convenient.

However, the business flow revealed that the buyer does not know how the supplier manages its inventory.

When a buyer creates an order, the buyer only expresses a commercial intention:

```text
Buyer wants to purchase:

- Product A
- Product B
- Product C

from Supplier X
````

The buyer has no knowledge about:

- Supplier warehouse structure
- Product stock distribution
- Inventory availability by warehouse
- Which warehouse should fulfill the order

The supplier owns the inventory organization and decides how products are physically fulfilled.

Example:

```text
Supplier A

Warehouse 1:
    Product A - 100 units
    Product B - 50 units

Warehouse 2:
    Product C - 20 units
```

An order may require products distributed across multiple warehouses.

Therefore:

```text
Order -> Warehouse
```

does not accurately represent the business relationship.

The real relationship is:

```text
Order
    |
    +-- Order Items
            |
            +-- Inventory Allocation
                    |
                    +-- Warehouse
```

## Considered alternatives

### Store warehouse_id directly in orders

Example:

```sql
orders
(
    id UUID,
    buyer_id UUID,
    supplier_id UUID,
    warehouse_id UUID
)
```

#### Pros

- Simple queries.
- Easy warehouse validation.
- Straightforward implementation.

#### Cons

- Assumes one order belongs to one warehouse.
- Couples commercial intent with physical fulfillment.
- Does not support orders fulfilled from multiple warehouses.
- Requires the buyer flow to know supplier inventory structure.
- Makes order creation responsible for logistics decisions.

### Assign warehouse during order creation

The system could automatically select a warehouse while creating the order.

Example:

```text
Create Order
        |
        v
Find warehouse
        |
        v
Create order with warehouse_id
```

#### Pros

- Warehouse information exists immediately.
- Simplifies later processing.

#### Cons

- Mixes order creation with inventory allocation.
- Requires inventory availability checks during order creation.
- Couples Orders and Inventory modules.
- Prevents future fulfillment strategies.
- Makes warehouse selection part of the buyer workflow.

### Assign warehouses during fulfillment

Keep orders independent from inventory location.

Example:

```text
Order

Supplier X
Items:
    Product A x5
    Product B x2


Fulfillment allocation:

Warehouse 1:
    Product A x5

Warehouse 2:
    Product B x2
```

#### Pros

- Keeps Order focused on commercial intent.
- Allows multiple warehouses per order.
- Keeps inventory ownership inside the Inventory domain.
- Supports future fulfillment strategies.
- Matches real supplier operations.

#### Cons

- Requires an additional allocation step.
- Requires querying inventory before fulfillment.

## Decision: Warehouse assignment belongs to fulfillment

The `Order` aggregate will not contain `warehouse_id`.

The order model represents only the commercial transaction:

```sql
orders
(
    id UUID,
    buyer_id UUID,
    supplier_id UUID,
    status order_status,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

Order items represent requested products:

```sql
order_items
(
    id UUID,
    order_id UUID,
    product_id UUID,
    quantity INTEGER
)
```

Warehouse assignment is introduced later through an inventory allocation concept.

Example:

```sql
inventory_allocation
(
    id UUID,
    order_item_id UUID,
    warehouse_id UUID,
    quantity INTEGER
)
```

The allocation process determines:

- From which warehouse stock will be taken.
- How much quantity each warehouse contributes.
- Whether fulfillment can proceed.

## Domain boundaries

The responsibility separation is:

### Orders module

Responsible for:

- Buyer purchase intent.
- Supplier relationship.
- Requested products.
- Order lifecycle.

It does not know:

- Warehouse structure.
- Stock distribution.
- Inventory allocation rules.

### Inventory module

Responsible for:

- Stock availability.
- Warehouse inventory.
- Reservation.
- Allocation decisions.

It determines:

```text
Order Item
        |
        v
Warehouse
```

## Design principles

- Commercial concepts and physical fulfillment concepts must remain separated.
- The buyer should not require knowledge of supplier internal operations.
- Warehouse selection is an inventory decision, not an order creation decision.
- Aggregates should only contain information they own.
- Cross-module communication must happen through explicit ports.

## Benefits

- Supports orders fulfilled by multiple warehouses.
- Preserves bounded-context separation between Orders and Inventory.
- Prevents unnecessary coupling between buyer workflows and supplier logistics.
- Allows future optimization strategies:

  - nearest warehouse selection
  - cost optimization
  - stock balancing
  - partial fulfillment
- Keeps the Order aggregate simpler and more stable.

## Trade-off

Fulfillment requires an additional allocation step before inventory can be reserved or dispatched.

This complexity is accepted because warehouse assignment is a logistics concern owned by inventory management, not a responsibility of order creation.
