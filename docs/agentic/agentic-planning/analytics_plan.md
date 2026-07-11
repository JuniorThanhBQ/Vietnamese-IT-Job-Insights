# Trend Analytics Execution Plan - Phase 4

This document outlines the detailed plans, metrics design, caching mechanisms, and development tasks for Phase 4: Trend Analytics API.

---

## 1. Metrics & Data Aggregation Design

The analytics system will expose a set of statistical trends derived from the active jobs database. We will calculate the following core metrics:

### A. Salary Trends by Seniority
* **Logic:** Calculate the average `salary_min` and `salary_max` grouped by `seniority` (where `salary_currency` is normalized, e.g., converted to VND or USD, or calculated separately for VND).
* **SQL Output Schema:**
  ```json
  [
    {"seniority": "Junior", "avg_min_vnd": 15000000.0, "avg_max_vnd": 25000000.0, "job_count": 120},
    {"seniority": "Senior", "avg_min_vnd": 40000000.0, "avg_max_vnd": 65000000.0, "job_count": 85}
  ]
  ```

### B. Tech Stack Demand
* **Logic:** Count the number of jobs containing specific key terms in their title, description, requirements, or `raw_metadata.tags`.
* **Keywords list:**
  * Frontend: `React`, `Angular`, `Vue`, `TypeScript`, `Next.js`
  * Backend: `Python`, `Golang` (or `Go`), `Node.js` (or `Node`), `Java`, `PHP`, `.NET` (or `C#`)
  * Infrastructure: `Docker`, `Kubernetes` (or `K8s`), `AWS`, `Azure`
* **SQL Output Schema:**
  ```json
  {
    "python": 145,
    "react": 182,
    "golang": 64
  }
  ```

### C. Remote Policy Distribution
* **Logic:** Count occurrences of remote policies (`Remote`, `Hybrid`, `Onsite`, `Unknown`).
* **SQL Output Schema:**
  ```json
  {
    "Remote": 45,
    "Hybrid": 120,
    "Onsite": 210,
    "Unknown": 12
  }
  ```

### D. Location Distribution
* **Logic:** Group jobs by city/region extracted from the job address (e.g. `Hồ Chí Minh` / `HCM`, `Hà Nội`, `Đà Nẵng`).
* **SQL Output Schema:**
  ```json
  {
    "Hồ Chí Minh": 280,
    "Hà Nội": 190,
    "Đà Nẵng": 55,
    "Other": 15
  }
  ```

---

## 2. Caching Infrastructure (Redis)

We will use the **Cache-Aside** strategy. The Redis Cache Service will be structured as:

* **Redis URL:** Loaded from `settings.REDIS_URL`.
* **Client:** Non-blocking `redis.asyncio` client to perform async Redis operations.
* **Key Naming Convention:** `job_insights:analytics:{metric_name}`.
* **TTL (Time-To-Live):** 12 hours (43,200 seconds) up to 24 hours.

---

## 3. Step-by-Step Implementation Tasks

### Step 1: Create Redis Caching Helper Service
* Create a file `backend/app/models/redis_client.py` (or similar) to initialize the async Redis client:
  ```python
  import redis.asyncio as aioredis
  from app.config import settings

  redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
  ```
* Create a caching service `backend/app/modules/jobs/cache_service.py` to get, set, and delete keys.

### Step 2: Implement SQL Queries in Repository
* Write SQLAlchemy queries inside [repository.py](../../backend/app/modules/jobs/repository.py):
  * `get_salary_trends_by_seniority(db)`
  * `get_remote_policy_distribution(db)`
  * `get_location_distribution(db)`
  * `get_tech_stack_demand(db, keywords)`

### Step 3: Implement Business Logic Service (with Cache-Aside)
* Create `backend/app/modules/jobs/analytics_service.py` (or add methods to `JobService`):
  * Method `get_analytics_overview(db)`:
    * Try to fetch `job_insights:analytics:overview` from Redis.
    * If found: Deserialize JSON and return.
    * If not found (cache miss):
      * Run the 4 database queries concurrently (using `asyncio.gather`).
      * Combine results into a single payload.
      * Serialize to JSON and store in Redis with TTL = 12 hours.
      * Return the payload.

### Step 4: Expose FastAPI Route
* Expose `GET /api/v1/jobs/analytics` in [routers.py](../../backend/app/modules/jobs/routers.py).
* Returns `JSON` containing the unified analytics overview.

### Step 5: Write Tests
* Create `backend/tests/test_analytics.py` (or similar).
* Mock PostgreSQL database session return values.
* Mock Redis `get` and `set` methods.
* Verify:
  * Cache miss triggers database queries and updates Redis.
  * Cache hit returns cached values directly without hitting the database.
