# Backend Agentic Specifications & Architecture Guidelines

This document supplements the main root [AGENTS.md](Vietnamese-Software-Engineer-JD-Insights/AGENTS.md) and defines specific rules, folder organization, and linting guidelines for the backend FastAPI project located in the `backend/` directory.

---

## 1. Directory Structure: Layered by Modules

The backend code under `backend/app/` must be structured as a **Layered Architecture within Modules**. All business-specific logic resides under a `modules` directory.

```
backend/app/
├── main.py                 # FastAPI application entrypoint
├── config.py               # Global settings & configuration loader
├── models/
│   └── db_models.py        # Central SQLAlchemy declarative base and models
└── modules/
    ├── __init__.py
    └── <module_name>/      # e.g., jobs, companies, users
        ├── __init__.py
        ├── models.py       # Module-specific models/schemas (Pydantic / DB)
        ├── repository.py   # Data access layer (SQLAlchemy queries)
        ├── services.py     # Business logic layer
        ├── views.py        # API serialization and request/response processing
        └── routers.py      # Route registrations
```

Each module must implement the following 5 distinct layers:

1. **`routers` (API Endpoints):**
   * Responsible only for registering URL routes and managing FastAPI path configurations.
   * Hands off control immediately to the `views` layer.
2. **`views` (Serialization & Presentation):**
   * Handles request validation, HTTP exceptions, and serialization/deserialization (using Pydantic schemas).
   * Transforms raw API payloads to Python structures and vice versa.
   * Calls the `services` layer for business operations.
3. **`services` (Core Business Logic):**
   * Implements the actual domain logic, business validations, and complex flows.
   * Coordinates calls between multiple repositories or external integrations.
   * Does not perform direct SQL queries or database session transactions.
4. **`repository` (Data Access Layer):**
   * Contains all SQLAlchemy query logic (async execution, filters, updates, joins).
   * Acts as the interface between the Python domain models and the database.
   * Should never contain business rules.
5. **`models` (Declarative Schema):**
   * Defines database structures or module-specific data schemas (Pydantic).

---

## 2. Dependency Rules and Import Boundaries

To maintain clean separation of concerns:
* **Strict Flow Direction:** Imports must strictly flow downwards:
  $$\text{routers} \rightarrow \text{views} \rightarrow \text{services} \rightarrow \text{repository} \rightarrow \text{models}$$
* **No Direct Bypasses:** The `routers` or `views` layer must **never** call `repository` directly. They must go through `services`.
* **No Reverse Imports:** Lower layers must **never** import from higher layers (e.g. `services` must not import from `views` or `routers`).
* **Inter-Module Boundaries:** Modules should ideally call each other's `services` rather than importing and querying another module's `repository` directly.

---

## 3. Architecture Enforcement using Import Linter

We use `import-linter` to statically verify that our dependency rules are respected.

### Running the Import Linter
Run the linter inside the `backend/` directory:
```bash
lint-imports --config pyproject.toml
```

### Configuration
The linter contracts are configured inside `backend/pyproject.toml` under the `[tool.importlinter]` table. It enforces:
* **`containers = ["app.modules"]`**: Analyzes each module under `app.modules` independently.
* **`layers` list**: Checks the strict order of layers `routers` -> `views` -> `services` -> `repository` -> `models`.

---

## 4. Code Quality Management using Pylint

We use `pylint` (moderate strictness) to catch semantic bugs and maintain code cleanliness.

### Running Pylint
Run Pylint inside the `backend/` directory:
```bash
pylint app/
```

### Moderate Strictness Guidelines
To maintain developer velocity on this project while preserving correctness, Pylint is configured with the following rules:
* **Disabled Checks:**
  * `C0114` / `C0115` / `C0116` (Missing docstrings): Omitted to avoid boilerplates.
  * `R0903` (Too few public methods): Allowed for small DTO classes or data holders.
  * `R0913` (Too many arguments): Allowed to accommodate FastAPI endpoints with multiple query parameters or dependencies.
  * `R0917` (Too many positional arguments): Allowed to support multiple query params / filters in routes.
  * `C0103` (Invalid name): Allowed for SQLAlchemy fields and special framework variables (e.g., `id`, `db_session`).
  * `W0621` (Redefined outer name): Allowed to support pytest fixtures and FastAPI `Depends(...)`.
  * `W0613` (Unused argument): Allowed for interface conformity and FastAPI dependency hooks.
* **Enforced Checks:**
  * Unused imports (`W0611`).
  * Undefined variables (`E0602`).
  * Missing imports / Syntax errors / Type exceptions.
  * Maximum line length set to `120`.
  * Target score: `fail-under = 7.0`.

---

## 5. Commenting Standards
* **No Indiscriminate Commenting:** Do not write obvious, redundant, or boilerplate comments that simply restate what the code does.
* **Exceptions:** Comments are allowed only when explaining complex business logic, architectural constraints, non-obvious design decisions, or when resolving tricky bugs.
