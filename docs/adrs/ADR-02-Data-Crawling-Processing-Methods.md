# ADR-02: Playwright with Celery and the data crawling pipeline

## Status
Pending

## Context
The project collects job postings from IT recruitment websites such as TopDev and ITviec. These websites rely heavily on JavaScript to render their content, so a traditional HTTP crawler cannot always retrieve the required information.

The crawler also needs to run automatically at scheduled times, process many job pages, avoid duplicate records, and save the collected data into the project database. Since crawling is a long-running background task, it should not block the REST API.

## Decision
Use the following data crawling architecture:
* **Playwright** for browser automation and JavaScript rendering.
* **Celery** for asynchronous background task execution.
* **Celery Beat** for scheduling periodic crawling jobs.
* **SQLAlchemy ORM** for database operations.
* **PostgreSQL** for storing normalized job data.

The crawling workflow is:
1. Celery Beat schedules a crawling task.
2. Celery Worker starts Playwright.
3. Playwright visits the job listing pages.
4. The crawler extracts job URLs and crawls each job detail page.
5. The extracted data is normalized and validated.
6. Duplicate records are checked before saving.
7. SQLAlchemy stores the final data in PostgreSQL.

## Rationale
1. Playwright can render JavaScript pages, making it suitable for modern recruitment websites.
2. Celery executes crawling tasks in the background, keeping the API responsive.
3. Celery Beat provides a simple way to schedule recurring crawling jobs.
4. SQLAlchemy simplifies database access and integrates well with FastAPI.
5. PostgreSQL is reliable for storing structured job information and supports future data analysis.

## Consequences
### Positive
* The crawling process is independent from the web application.
* Scheduled crawling keeps job data up to date automatically.
* Background tasks improve API responsiveness.
* The pipeline can be extended with AI processing, such as embedding generation or RAG indexing.

### Negative
* More infrastructure components are required, including Celery and a message broker.
* Browser automation consumes more CPU and memory than HTTP requests.
* Changes to the target websites may require updates to the crawler.

## Decision Date
Pending until 21:00 – 10/07/2026
