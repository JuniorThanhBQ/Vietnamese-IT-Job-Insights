# ADR-05: Trend Analytics Aggregation and Caching Strategy

## Status
Approved

## Context
The project goals require providing data analytics on IT recruitment trends in Vietnam (e.g., average salaries by seniority, demand percentages for specific technical skills, distribution of remote/hybrid work options, and job locations).

However, our low-resource host system (8GB RAM, i7 Gen 4 CPU, slow disk I/O) poses challenges:
1. Running complex relational SQL aggregation queries (such as `AVG`, `COUNT`, and `GROUP BY` across thousands of jobs) dynamically on every user API request would cause CPU spikes and slow down other REST API requests.
2. Since secondary fields like skills and detailed locations are stored in a `JSONB` column (`raw_metadata`) to optimize writes and database size (as decided in ADR-03), parsing these fields requires JSON path extractions, which are computationally heavier than standard column queries.
3. Market trends (e.g., salary levels, technology demand) are historical and change slowly. Real-time updates on every API call are unnecessary.

## Decision
We will implement the following trend analytics and caching strategy:

1. **In-Database Aggregations:** Perform all statistical calculations (averages, counts, percentages) directly in PostgreSQL 17 using optimized SQL queries via SQLAlchemy ORM. This minimizes memory overhead in the FastAPI application.
2. **JSONB Path Extractions:** Use PostgreSQL JSONB operators (like `->>` or `jsonb_to_recordset`) or keyword text-search checks inside SQLAlchemy to analyze technology stack trends (e.g., counting occurrences of tags or strings like "React", "Python", "Golang", "Kubernetes" in job descriptions, requirements, and `raw_metadata`).
3. **Redis Caching (Cache-Aside Pattern):**
   * Cache the JSON responses of the trend analytics endpoints in our lightweight Alpine Redis instance.
   * Set a strict Time-To-Live (TTL) of **12 to 24 hours** for all cached analytics.
   * On API request:
     * Check Redis for the key. If it exists (cache hit), return the deserialized JSON data immediately (latency < 5ms).
     * If not found (cache miss), execute the PostgreSQL aggregation queries, save the serialized JSON result to Redis with the specified TTL, and return the data.
4. **Endpoint Decoupling:** Keep analytics endpoints separated from search and CRUD endpoints, so that cache eviction policies can be managed independently.

## Rationale
1. **Low Resource Consumption:** Redis caching reduces database read cycles by 99%, preserving CPU and RAM for other processes (such as crawler execution and pgvector searches).
2. **Acceptable Latency:** A cache-aside approach ensures lightning-fast page loading times for the frontend dashboard.
3. **Eventual Consistency:** Since recruitment trends change weekly or monthly, a 12-to-24-hour cache latency has zero negative impact on user experience or data correctness.

## Consequences
### Positive
* Lightning-fast response times (< 5ms) for trend analytics APIs.
* Negligible CPU load on PostgreSQL under high API traffic.
* Simple cache-aside implementation using Redis.
* High adaptability to additional analytics fields since the backend code handles JSON serialization.

### Negative
* Analytics data is not real-time (eventual consistency up to 24 hours).
* Requires extra logic to serialize and deserialize data models to and from Redis.

## Decision Date
Approved on 11/07/2026
