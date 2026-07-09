# ADR-01: Client-Server Architecture with a Layered Backend Architecture

## Status
Pending

## Context
This project is an IT job search platform for software engineers. It also includes AI-powered features such as Retrieval-Augmented Generation (RAG) and Semantic Search, making Python a suitable choice for the backend. The project follows a controlled Vibe Coding approach. Therefore, separating the frontend and backend into different codebases is practical. In addition, the project is based on my experience with Client-Server architecture using Python and JavaScript.

## Decision
Using **Client-Server architecture**:
* Client: React with Vite
* Server: FastAPI with REST API and Pydantic

Using **Layered Architecture** for the backend:
* Presentation Layer (Controllers)
* Business Logic Layer (Services)
* Data Access Layer (SQLAlchemy ORM)

## Rationale
1. FastAPI provides an efficient way to build APIs for complex RAG and Semantic Search workflows.
2. The Client-Server architecture allows the frontend and backend to be developed independently, reducing development dependencies.
3. The Layered Architecture separates responsibilities clearly and makes the source code easier to organize by feature modules.
4. The Client-Server architecture is flexible for deployment because it is supported by many cloud platforms.
5. It is more suitable for a personal project than a Microservices architecture.

## Consequences
### Positive
* Better separation between the frontend and backend.
* Easier to maintain, extend, and modify business logic.
* If the client application fails, the backend services can continue running independently.
* Supports independent deployment of the frontend and backend.

### Negative
* Network communication introduces latency because the system is distributed.
* The backend may suffer from common layered architecture issues such as the **Sinkhole Anti-Pattern**, **God Objects**, and limited availability if deployed as a single server.

## Decision Date
Pending until 21:00 – 10 July 2026
