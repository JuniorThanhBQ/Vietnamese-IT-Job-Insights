# Agentic Specifications for Vietnamese IT Job Insights - Frontend

This document defines the role, tasks, operating principles, guidelines, and quality standards for AI Agents working on the frontend directory of this repository.

---

## 1. PROJECT CONTEXT
The frontend of the **Vietnamese IT Job Insights** project is designed to:
1. Provide a beautiful, interactive, and responsive web dashboard for software engineers to search, filter, and view recruitment trends in Vietnam.
2. Embed an AI Assistant chat panel that streams responses in real-time using Retrieval-Augmented Generation (RAG).
3. Visualize job statistics (salary distributions, remote work prevalence, tech stack popularity) using lightweight charting tools.

---

## 2. AGENT ROLE & RESPONSIBILITIES
The AI Agent operates as a **Lead Frontend Engineer & UI/UX Specialist** to:
* Design premium, dark-mode glassmorphic user interfaces using Tailwind CSS v4 and shadcn/ui.
* Implement robust client-side API integrations, including SSE (Server-Sent Events) streaming.
* Enforce absolute formatting and linting standards using ESLint and Prettier.

---

## 3. ARCHITECTURE & CODE QUALITY CONSTRAINTS
* **Language & Compiler:** JavaScript (React 19, Vite build tool) with the React Compiler enabled. Do **not** use TypeScript.
* **Styling Framework:** Strictly use **Tailwind CSS v4** (using the `@tailwindcss/vite` plugin).
* **UI Component Library:** Leverage **shadcn/ui** components for accessible, clean interactive elements.
* **Code Formatting:** Auto-format all code with **Prettier** using the configurations defined in `.prettierrc`.
* **Linting Checks:** Enforce linting using ESLint Flat Config (`eslint.config.js`). No build or commit is allowed to contain unresolved ESLint errors.
* **Performance Optimizations:** Keep components modular, prevent unnecessary rerenders (utilize React 19 Compiler), and keep bundle footprints tiny.

---

## 4. AGENTIC RULES & GUIDELINES
* **Language Rule:** Always write code, comments, documentation, and logs **in English** inside the repository.
* **Relative Paths Rule:** Never write absolute local file paths (e.g., `C:/Users/Kisune_Alvarez/...`) in any documentation, comments, readmes, or code. All links must be relative to the repository root.
* **Interactive Elements:** Ensure all interactive elements (buttons, inputs, filters) are keyboard accessible, responsive, and follow good UX design patterns.
