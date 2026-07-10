# Frontend Agent Specifications

This document defines the user experience, design guidelines, file organization, and quality standards for AI Agents working inside the `frontend/` directory.

---

## 1. Role & Scope
The frontend provides a modern web interface for users to search jobs using natural language (Semantic Search / RAG), browse market analytics (salaries, skills, locations), and view Vietnamese Software Engineer JD Insights.

---

## 2. Technology Stack & Design System
* **Core:** React 19, Vite, ES6 Javascript.
* **Styling:** Use Vanilla CSS for custom, high-fidelity styles. Avoid TailwindCSS unless explicitly requested.
* **Typography:** Sleek modern typography (e.g., from Google Fonts like Inter or Outfit) instead of default system fonts.
* **Color Palette:** Curated modern color palettes (e.g. customized HSL colors, sleek dark modes, glassmorphism gradients) rather than generic defaults.

---

## 3. Premium UI/UX Guidelines
To deliver a premium, state-of-the-art feel to the developer:
1. **Micro-Animations:** Add subtle transitions for hovers, button clicks, and loading states.
2. **Interactive Elements:** Use smooth hover effects, active state feedback, and responsive transitions.
3. **No Placeholders:** Never use fake images or unstyled layout grids. If images are required, request dynamic assets or generate high-quality visual aids.
4. **Responsive Layouts:** Enforce responsive web design principles covering mobile, tablet, and desktop viewports.

---

## 4. SEO & Accessibility Best Practices
* **Title & Meta Tags:** Maintain descriptive title tags and meta descriptions on active views.
* **Semantic HTML:** Use proper HTML5 tags (`<header>`, `<main>`, `<section>`, `<nav>`, `<article>`, `<footer>`) instead of nested standard `<div>` elements.
* **Heading Hierarchy:** Use a single `<h1>` per page, following down with sequential headings (`<h2>`, `<h3>`).
* **Interactive Elements IDs:** Ensure all buttons, inputs, and form controls have unique, descriptive `id` attributes for testing and automation.

---

## 5. Coding Standards & Lints
* **Linting Enforcements:**
  * All frontend code must satisfy the configuration set inside `frontend/eslint.config.js`.
  * Ensure there are zero ESLint warnings or errors (`npm run lint` must pass cleanly).
* **Secret Checking:** Strict compliance with security plugins (`eslint-plugin-no-secrets` and `eslint-plugin-security`). Never commit raw keys, credentials, or API endpoints.
* **Commenting Rule:**
  * **No Indiscriminate Commenting:** Avoid comments that simply describe JSX layouts or standard React Hooks.
  * Only comment to document complex state flows, graph render computations, or non-obvious styling overrides.
* **Privacy & Relative Paths:** Absolute paths containing local user directories (e.g. `C:/Users/Kisune_Alvarez/...`) are strictly forbidden. All links must be relative to the repository root.
