# Vietnamese-Software-Engineer-JD-Insights
This project was created for two purposes. The first purpose is to provide an environment in which I can improve my experience with RAG, semantic search, and vector databases. The second purpose is to address the need for insights into current Software Engineering job deal trends by developing a system based on the research paper at [An LLM-Powered Agent for Real-Time Analysis of the Vietnamese IT Job Market](https://arxiv.org/pdf/2511.14767)

## I. Project Description
### 1. Main goal
The main goal of this project is to develop a platform where applicants can find open software engineering jobs on TopDev and ITViec. Moreover, the platform will have a virtual assistant that can help applicants identify trends and companies' hiring needs.

### 2. Aim
There are three aim for this project based on the main goal.
1. Firstly, this platform is a Website that helps users search for Software Engineering-related job opportunities on TopDev and ITviec but does not support automatic CV submission.
2. Secondly, there will be a virtual assistant help you explore information about Software Engineering jobs hiring like jobs deal trend, average minimum experience required, and more.
3. Finally, The original purpose of this project is to improve practical skills in data analytics and explore AI techniques, particularly Retrieval-Augmented Generation and Semantic Search. Moreover, I also aim to learn how to develop an application following the Vibe Coding approach and enhance Agile project management capabilities.

## II. Technologies
Note: Based on the research [An LLM-Powered Agent for Real-Time Analysis of the Vietnamese IT Job Market](https://arxiv.org/pdf/2511.14767), this project proposes using some technologies in the table below. The official technologies will be announced in the near future.

| Core structure | Technology | Version | Reason for Use |
| :--- | :--- | :--- | :--- |
| **Backend** | FastAPI (with SQLAlchemy and Pydantic) | FastAPI 0.116+, SQLAlchemy 2.x,Pydantic 2.x | Provides a lightweight, high-performance REST API for serving job data, semantic search, and AI assistant endpoints. FastAPI integrates naturally with LangChain and asynchronous Python applications. |
| **Frontend** | React (Vite) | React 19 + Vite 7 | Builds a responsive Single-Page Application (SPA) for job search, dashboard visualization, and AI-assisted interaction while offering fast development and optimized build performance. |
| **Database** | PostgreSQL (with pgvector) | PostgreSQL 17 + pgvector 0.8+ | Stores structured job information together with vector embeddings, enabling both traditional SQL queries and semantic similarity search within a single database engine. |
| **Data Collector** | Playwright | 1.54+ | Automates crawling of job postings from TopDev and ITviec while handling JavaScript-rendered pages and modern anti-bot mechanisms. This follows the data collection approach described in the reference paper. |
| **RAG and Semantic Search** | LangChain + Gemini API | LangChain 0.3+ Gemini 2.5 | Builds Retrieval-Augmented Generation pipelines, semantic search, prompt orchestration, and AI tools. Gemini performs information extraction, career consultation, and reasoning over retrieved job postings. |
|Embedding Model | Gemini Embedding | Gemini Embedding-001 | Converts job descriptions into dense vector representations for semantic similarity search, retrieval, and Retrieval-Augmented Generation (RAG). The generated embeddings are stored in PostgreSQL using pgvector |
| Visualization | Chart.js | 4.x | Provides interactive visualizations of hiring trends, technology demand, salary distribution, and experience requirements to improve data interpretation for users. |


## IV. System Architecture
The planned architecture will be client-server. The backend will be organized using a layered architecture. The system will prioritize two key criteria: performance and availability. In addition, design patterns will be applied to ensure the maintainability of the source code.
A detailed description of the system architecture is provided in [ADR-01-Software-Architecture.md](ADR-01-Software-Architecture.md) <br>
[Architecture overview image (not available)](docs/architectures/)

## V. Showcase
Will be available after the project is finished

## VI. How to use it
Will be available after the project is finished

## VII. Deployment
Will be available after the project is finished

## VIII. Documentation
- [ADRs](docs/adrs/)
- [API Documentation](docs/apis/)
- [Architecture](docs/architecture/)
- [References](docs/references/)
- [Weekly Report](docs/weekly-report/)
- [Agentic Usage History](docs/agentic-history/)
