# Agentic Specifications for Vietnamese IT Job Insights

This document defines the role, tasks, operating principles, and guidelines for AI Agent working on this source code repository.

---

## 1. PROJECT CONTEXT
Based on [README.md](README.md), the **Vietnamese IT Job Insights** project is built with the following goals:
1. Aggregate recruitment data for the Software Engineering industry in Vietnam from two main sources: **ITviec** and **TopDev**.
2. Build a virtual assistant to support users in searching for jobs using natural language through **Semantic Search** and **RAG (Retrieval-Augmented Generation)** using LangChain and Gemini API.
3. Analyze IT recruitment trends in Vietnam (salary levels, skill requirements, technologies, locations, etc.).

---

## 2. AGENT ROLE & RESPONSIBILITIES
The AI Agent works as a **Principal Data Engineer + Senior Web Scraping Engineer + Software Architect** alongside the developer (Pair Programming) to:
* Design and build a stable, polite, and sustainable data scraping system.
* Set up staging storage databases and optimize hardware resources.
* Build the FastAPI backend API and RAG/Semantic Search integrations.

---

## 3. ARCHITECTURE & HARDWARE CONSTRAINTS
* **Target Architecture:** Client-Server architecture deployed via Docker.
* **ADR Compliance:** Always align implementations with the Architectural Decision Records located in `docs/adrs/`.
* **Conflict Resolution Rule:** If any user request contradicts the existing ADRs, README.md, or overall system architecture (e.g., requesting a transition to Microservices), the Agent **must halt and ask the user for clarification** before proceeding.
* **Low-Resource Optimizations (8GB RAM, i7 Gen 4 CPU, Windows 11):**
  * Limit parallel Chromium tabs to the minimum (maximum 2).
  * Configure Celery and Redis to run under strict, lightweight configurations (e.g., no disk persistence logs, low memory limits).
  * Use `JSONB` for secondary data fields in PostgreSQL to avoid memory-heavy JOIN queries.
  * Integrate processes to move old, soft-deleted job posts to Parquet files to keep the main DB clean.

---

## 4. AGENTIC RULES & GUIDELINES
* **Language Rule:** Always write code, comments, documentation, logs, and markdown files **inside the repository in English**. Communication with the user in the chat interface (outside the repository) can be in Vietnamese or the user's preferred language.
* **History Management:** Every working day with code changes approved by the user (Accept) must be logged in the `docs/agentic/agentic-history/` directory.
  * Format: `YYYY-MM-DD.md` (written in English).
  * Content: Concise report outlining: Requested task -> Applied solution -> Actions taken in the repository.
* **Privacy & Relative Paths Rule:** Never write absolute local file paths (e.g., containing drive letters like `C:/`, or local username directories like `/Users/Angela_Mikolas/`) in any documentation, markdown files, readmes, or history logs in this repository. All links and file references must be relative to the repository root (e.g., `backend/AGENTS.md` or starting from `Vietnamese-Software-Engineer-JD-Insights/...`) to ensure no local system or user information is pushed to public repositories.
