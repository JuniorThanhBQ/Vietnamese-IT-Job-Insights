# ADR-03: Database Design, Categorical Enums, and pgvector Integration

## Status
Approved

## Context
The project requires a structured database schema to store jobs and companies scraped from ITviec and TopDev.
Moreover, it integrates Retrieval-Augmented Generation (RAG) and Semantic Search, which require storing dense vector representations (768-dimensional embeddings generated from job descriptions).

However, we face strict hardware constraints:
1. **Low Memory (8GB RAM):** Running a separate database for relational data (PostgreSQL) and a separate vector database (e.g., Qdrant, Milvus) would consume an additional 1GB - 2GB of RAM, exceeding limits.
2. **Slow I/O & CPU:** Repeated crawler iterations can cause write latency and CPU usage spike when updating many-to-many relationships or rebuilding vector indices.
3. **Data Decay:** Soft-deleted jobs (expired/removed postings) accumulate over time, slowing down relational queries.
4. **Data Redundancy:** Categorical attributes (`remote_policy`, `seniority`, `employment_type`, `salary_currency`) are highly repetitive across postings.

## Decision
We will implement the following database design and vector search strategy:

1. **Single Source of Truth (SSoT):** PostgreSQL 17 will act as the SSoT. All job postings, company information, and vector embeddings will reside in a single database.
2. **Simplified relational schema:**
   * Create two primary tables: `companies` and `jobs`.
   * Store secondary lists (`skills`, `benefits`, `detailed locations`) in a `raw_metadata` `JSONB` column inside the `jobs` table, rather than creating complex many-to-many intermediate tables (e.g., `job_skills`, `job_locations`).
3. **Categorical Fields Standardization:**
   * Standardize categorical fields (`remote_policy`, `seniority`, `employment_type`, `salary_currency`) using Python Enums (`enum.Enum`) at the application/code level.
   * Add PostgreSQL `CheckConstraint` validation on these columns to guarantee data sanitization at the database level.
4. **In-Database Vector Search:**
   * Use the **`pgvector`** extension in PostgreSQL 17 to store and query embeddings.
   * Store 768-dimensional vectors in a separate 1-to-1 table `job_embeddings` linked to `jobs(id)` via a foreign key, and build HNSW index parameters during low-traffic periods.
5. **Data Archiving Policy:**
   * Keep only active jobs (`is_active = True`) and recently closed jobs (closed < 90 days) in PostgreSQL.
   * Periodically (e.g., monthly), export expired jobs older than 90 days to compressed **Parquet** files on local disk (for future historical analytics via DuckDB/Polars), and perform a `HARD DELETE` in PostgreSQL.
6. **Change Detection via SHA-256 Hash:**
   * Compute a `content_hash` (`SHA-256`) of the core job attributes (`title`, `salary_raw`, `description`, `requirements`) before saving.
   * Bypass database `UPDATE` writes if the scraped posting's hash matches the existing record in the database.

## Rationale
1. **Memory efficiency:** Using `pgvector` inside PostgreSQL 17 avoids spinning up another heavy database container, saving ~1GB - 2GB of RAM.
2. **Write performance:** Reducing write operations from $N$ relationship inserts to a simple 2-table UPSERT speeds up crawler throughput and protects disk lifespan.
3. **Index performance:** Limiting the active dataset in PostgreSQL (by archiving older soft-deleted posts to Parquet) keeps active indexes small and ensures API query latencies remain under 10ms.
4. **Change detection:** The SHA-256 hash avoids writing redundant data to disk and helps identify when employers silently modify job requirements.

## Consequences
### Positive
* Extremely low memory usage under the 8GB RAM limit.
* Fast crawler writes and simple transactional operations.
* Simple schema modification since extra crawled fields can be put directly into `raw_metadata`.
* Decoupled analytical querying (using Parquet files offline) keeps the transactional database clean.

### Negative
* Queries looking for specific skills or locations using pure SQL will require JSONB path expressions instead of standard relational `JOIN` operations.
* Running HNSW index generation on a 4th Gen i7 CPU will take longer, requiring scheduling.

## Decision Date
Approved on 10/07/2026
