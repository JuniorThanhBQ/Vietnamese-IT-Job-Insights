# ADR-06: Frontend Architecture, Styling Decisions, and Quality Controls (JavaScript, Tailwind CSS 4, shadcn/ui)

## Status
Approved

## Context
The project goals require building a premium, modern, and highly interactive web frontend to allow users to search for software engineering jobs in Vietnam, consult an AI assistant, and view market trend analytics.

The user has explicitly specified a change in the technology stack and quality controls:
1. **Language:** JavaScript (using Vite build and the modern React Compiler) instead of TypeScript, to speed up execution and reduce compilation strictness overhead.
2. **Styling:** Tailwind CSS v4 (which utilizes the modern `@tailwindcss/vite` plugin instead of PostCSS) to provide rapid utility-first styling.
3. **UI Components:** shadcn/ui components (accessible Radix primitives with Tailwind styling) to build a premium, uniform, and state-of-the-art UI dashboard.
4. **Code Quality & Formatting:** Strict ESLint configuration combined with **Prettier** to enforce code quality and automated, consistent layout formatting.

## Decision
We will adopt the following frontend architecture and quality controls:

1. **Core Framework:** Use **Vite** to initialize and build a **React 19** application using **JavaScript** with the **React Compiler** enabled for automatic dependency caching (eliminating the need for manual `useMemo` and `useCallback`).
2. **Styling & Components:**
   * Integrate **Tailwind CSS v4** using the new Vite plugin framework (`@tailwindcss/vite`). This provides native CSS-based configuration and extremely fast styling hot-reloads.
   * Adopt **shadcn/ui** for modular, highly polished, accessible UI primitives (e.g., Dialogs, Buttons, Cards, Inputs, Tables).
3. **Code Formatting & Quality Controls:**
   * Configure **ESLint** (Flat Config `eslint.config.js`) for React 19 syntax checking, react-hooks validation, and unused variable rules.
   * Integrate **Prettier** for automated code formatting (semi-colons, single quotes, double spaces, trailing commas).
   * Integrate Prettier with ESLint using `eslint-config-prettier` to ensure formatting rules do not clash with lint rules.
4. **AI Chat Client:** Connect to our FastAPI Server-Sent Events `/jobs/chat` stream using native asynchronous Fetch API readers (`ReadableStream`) to stream responses token-by-token directly into the UI state.

## Rationale
1. **Lightweight Developer Workflow:** JavaScript (with React Compiler) reduces TypeScript compiler overhead and memory footprint in development.
2. **Premium Design Aesthetics:** Combining Tailwind CSS v4 utility classes with shadcn/ui components allows us to quickly construct beautiful dark-mode glassmorphic layouts, animated sidebars, and clean analytics displays.
3. **Consistency:** Prettier formatting combined with ESLint flat configuration guarantees that the JavaScript source code is clean, consistent, and free from common bugs.

## Consequences
### Positive
* Lightning-fast Vite hot-reload times.
* Rapid component assembly using shadcn/ui copy-paste components.
* Strict code formatting consistency maintained by Prettier.
* Automatic optimization of rendering re-evaluations via the React Compiler.

### Negative
* JavaScript lacks compile-time strict type safety, which places a higher responsibility on ESLint checks.
* Managing shadcn/ui installation adds files (under a `components/ui/` directory) directly into the src structure, which must be organized properly.

## Decision Date
Approved on 11/07/2026
