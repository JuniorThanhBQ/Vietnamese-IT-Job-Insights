# Project Execution Plan - Vietnamese IT Job Insights

This document outlines the current state, core architectural alignment objectives, and the future development roadmap of the Vietnamese IT Job Insights project.

---

## 1. Accomplished Work
We have successfully built the complete architectural foundation, backend modules, database infrastructure, and crawler core:

* **Centralized Dependency & Environment Setup:**
  * Migrated all Python packages to [backend/pyproject.toml](../../../backend/pyproject.toml) using PEP 621 standards.
  * Implemented unified environment loading using Pydantic Settings in [backend/app/config.py](../../../backend/app/config.py) from `.env`.
* **Lightweight Local Infrastructure (Docker Compose):**
  * Configured PostgreSQL 17 with the `pgvector` extension, mapped to host port `5433` to prevent conflicts with local services.
  * Configured Alpine Redis 7 with strict memory constraints (`maxmemory 256mb`, LRU policy, no disk persistence log) for low-resource environments.
* **Modular Layered Backend Skeleton:**
  * Created clean modules under [backend/app/modules/](../../../backend/app/modules/) (`companies` and `jobs`) following the strict dependency flow: `routers` $\rightarrow$ `views` $\rightarrow$ `services` $\rightarrow$ `repository` $\rightarrow$ `models`.
  * Implemented Pydantic DTOs and SQLAlchemy repository layers utilizing async database connections ([backend/app/models/database.py](../../../backend/app/models/database.py)).
  * Ticked off automatic Swagger/ReDoc API schemas generation and exported to [docs/apis/api_v1.json](../../../docs/apis/api_v1.json).
* **Alembic Database Migrations:**
  * Initialized and configured Alembic for async migrations.
  * Created the initial database migration script to enable `pgvector` and construct SQLAlchemy tables.
* **Optimized Playwright & Selectolax Crawler Core:**
  * Built [crawler/base/crawler.py](../../../crawler/base/crawler.py) limiting concurrency to a maximum of **2 parallel tabs** and blocking media, image, stylesheet, and font assets to save RAM/CPU.
  * Built specialized high-performance Selectolax parsers for ITviec ([crawler/parser/itviec_parser.py](../../../crawler/parser/itviec_parser.py)) and TopDev ([crawler/parser/topdev_parser.py](../../../crawler/parser/topdev_parser.py)).
  * Implemented heuristic normalizers for salaries, seniority, remote policies, and contract types in [crawler/utils/normalizer.py](../../../crawler/utils/normalizer.py).
  * Built [crawler/pipelines/job_pipeline.py](../../../crawler/pipelines/job_pipeline.py) orchestrating the full fetch-parse-save transaction (with change detection via SHA-256 content hashes).
* **Quality Control & Linting:**
  * Enforced quality standards: Pylint rated at **10.00/10** and Import Linter showing **0 broken contracts**.
  * Drafted coding rules in root [AGENTS.md](../../../AGENTS.md), [backend/AGENTS.md](../../../backend/AGENTS.md), and [crawler/AGENTS.md](../../../crawler/AGENTS.md).

---

## 2. Key Objectives & Compliance Requirements
To ensure the system conforms to the user requirements and low-resource limitations:

* **Resource Preservation:**
  * Maximum 2 parallel tabs in Playwright browser at any given time.
  * Prevent Celery and Redis from consuming excessive memory by setting strict limit policies.
  * Store secondary job/company metadata fields using PostgreSQL `JSONB` to avoid heavy database JOIN queries on a low-spec system.
* **Anti-Scraping Evasion:**
  * Playwright requests must use modern user-agent rotation and randomized human-like delays (1.0 to 3.0 seconds).
  * Clean closing of browser pages immediately after extraction to prevent memory leaks.
* **Strict Quality & Architectural Boundaries:**
  * Code compliance: Python code must pass Pylint checks with high ratings.
  * Layer boundaries: Prevent modules from crossing layers (e.g. repositories importing routers). Checked via Import Linter contracts.
  * Absolute paths warning: No local drive letters (e.g. `C:/...`) or usernames in public files.
  * Clean code comments: Avoid comment clutter. Only comment when documenting complex logic.

---

## 3. Future Execution Roadmap

### Phase 1: Crawler Automation (Scheduling & Orchestration) [COMPLETED]
* **[x] Celery Integration:** Configure Celery workers connected to the Alpine Redis broker. Enforce strict memory limits (e.g., `worker_max_memory_per_child`) to prevent long-running crawler tasks from causing Out-Of-Memory (OOM) errors.
* **[x] List Scraping Logic:** Implement the pagination crawling logic to fetch job lists from ITviec and TopDev, extracting individual job URLs to feed into the existing [job_pipeline.py](../../../crawler/pipelines/job_pipeline.py).
* **[x] Beat Scheduler:** Configure Celery Beat to schedule recurring crawl jobs (e.g., running daily at low-traffic hours like 2:00 AM) to maintain an up-to-date database.
* **[x] Error Handling & Retries:** Implement exponential backoff for failed fetch attempts and proxy rotation triggers if 403/429 HTTP errors are encountered.


### Phase 2: Embedding Generation & Vector Search [COMPLETED]
* **[x] Embedding Pipeline:** Create a service to generate vector embeddings from job descriptions and requirements. To maintain low local resource usage, utilize a cloud-based API (like Gemini) rather than hosting heavy local embedding models.
* **[x] Database Vectorization:** Store generated embeddings in the PostgreSQL database using the `pgvector` extension.
* **[x] Similarity Search API:** Develop FastAPI endpoints utilizing `pgvector` operators (Cosine Distance or Inner Product) to query jobs matching specific technical descriptions or semantic concepts.


### Phase 3: RAG Integration (AI Chatbot) [COMPLETED]
* **[x] LangChain Orchestration:** Integrate LangChain to bridge the FastAPI backend with the Gemini API.
* **[x] Contextual Retrieval:** Build a retrieval chain that takes user queries, converts them to embeddings, fetches the top-K most relevant job postings via the Vector Search API, and feeds them into the prompt context.
* **[x] Assistant Endpoint:** Expose a streaming chat endpoint (`text/event-stream`) for the React frontend, allowing users to ask natural language questions (e.g., "What are the requirements for a Mid-level Python dev in Ho Chi Minh?").


### Phase 4: Trend Analytics API [COMPLETED]
* **[x] Statistical Aggregation:** Create specialized SQLAlchemy queries to calculate market trends: average salaries by seniority, demand percentages for specific tech stacks (e.g., React vs. Angular), and the prevalence of remote/hybrid work policies.
* **[x] Caching Strategy:** Since aggregations are computationally heavy for low-spec databases, cache the JSON responses of these analytics in Redis with a Time-To-Live (TTL) of 12-24 hours.


### Phase 5: React Frontend UI Development [COMPLETED]
* **[x] Framework & Styling:** Initialize a React 19 JavaScript project using Vite and React Compiler. Format using Prettier, utilizing Tailwind CSS v4 and shadcn/ui components.
* **[x] Data Visualization:** Integrate a lightweight charting library (like Recharts) to visualize the data provided by the Trend Analytics API.
* **[x] Chat Panel:** Build a reactive, streaming chat interface to communicate with the Phase 3 RAG Assistant endpoint.
* **[x] Job Dashboard:** Develop a clean, paginated dashboard for traditional job searching, filtering, and detailed job views.


### Phase 6: Docker Packaging & Archival Policies
* **Production Compose:** Finalize a `docker-compose.prod.yml` mapping the FastAPI backend, Celery workers, React frontend (served via Nginx), Postgres, and Redis into a single deployable stack.
* **Data Archival Cron:** To prevent the PostgreSQL database from bloating over time, write a scheduled task that queries jobs older than 60-90 days, exports them to compressed `.parquet` files for historical storage, and safely deletes them from the active database.
