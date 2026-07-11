# Frontend Development Execution Plan - Phase 5 (JS, Tailwind CSS 4, shadcn/ui)

This document outlines the detailed plans, project structure, styling setups, Prettier/ESLint configs, and step-by-step development tasks for building the React 19 JavaScript web frontend.

---

## 1. Project Directory Structure

We will create the React application under the `frontend/` directory at the repository root.

```
frontend/
├── eslint.config.js       # Modern ESLint Flat Config
├── .prettierrc            # Prettier formatting configurations
├── package.json           # Scripts and dependencies
├── vite.config.js         # Vite configuration (with @tailwindcss/vite plugin)
├── index.html             # Entry HTML
├── src/
│   ├── main.jsx           # Entry React mounting script
│   ├── App.jsx            # Main application layout orchestrator
│   ├── index.css          # Base CSS and Tailwind imports
│   ├── components/
│   │   ├── ui/            # shadcn/ui copy-paste components (Button, Card, etc.)
│   │   ├── JobCard.jsx    # Renders job listings
│   │   ├── ChatPanel.jsx  # Interactive streaming chatbot panel
│   │   └── Analytics.jsx  # Visualizes Recharts trend statistics
│   └── hooks/
│       ├── useChat.js     # Handles SSE stream fetching and state accumulation
│       └── useFetch.js    # Generic API call helper hook
```

---

## 2. Code Quality & Formatting Configurations

### A. Prettier Configuration (`frontend/.prettierrc`)
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

### B. ESLint Flat Config (`frontend/eslint.config.js`)
We will configure ESLint without TypeScript parsers, integrating React 19 rules and Prettier configuration compatibility.

```javascript
import js from "@eslint/js";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import prettierConfig from "eslint-config-prettier";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        window: "readonly",
        document: "readonly",
        console: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        ReadableStream: "readonly",
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      "react": reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
      "react/react-in-jsx-scope": "off", // React 19 does not require React in scope
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      "no-console": ["warn", { allow: ["warn", "error", "info"] }],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
  prettierConfig, // Disables all ESLint rules that conflict with Prettier
];
```

* Script definitions in `package.json`:
  * `"lint": "eslint src --ext .js,.jsx"`
  * `"format": "prettier --write \"src/**/*.{js,jsx,css}\""`

---

## 3. Styling & UI Components Setup

### A. Tailwind CSS v4 Setup
Tailwind CSS v4 introduces a new architecture integrated directly with Vite.
* **Dependencies:** `npm install tailwindcss @tailwindcss/vite`
* **Vite Config (`vite.config.js`):**
  ```javascript
  import { defineConfig } from 'vite';
  import react from '@vitejs/plugin-react'; // React plugin
  import tailwindcss from '@tailwindcss/vite'; // Tailwind v4 plugin

  export default defineConfig({
    plugins: [
      react(),
      tailwindcss(),
    ],
  });
  ```
* **Main CSS (`src/index.css`):**
  ```css
  @import "tailwindcss";
  ```

### B. shadcn/ui Initialization
* Run: `npx shadcn@latest init` to setup the paths and styles config.
* Select settings:
  * Style: Default
  * Base color: Slate
  * CSS variables: Yes
* Add components as needed:
  * `npx shadcn@latest add button card dialog input select separator table`

---

## 4. Step-by-Step Execution Tasks

### Step 1: Initialize Vite Project in `frontend/`
* Run: `npx -y create-vite@latest frontend --template react`
* Add React Compiler babel/vite plugin if desired, or let Vite React 19 handle default compilation optimization.
* Install dependencies: `recharts lucide-react clsx tailwind-merge`

### Step 2: Configure Code Quality Tools
* Create `frontend/.prettierrc` and `frontend/eslint.config.js`.
* Install linter dependencies: `npm install -D eslint eslint-plugin-react eslint-plugin-react-hooks eslint-config-prettier prettier`

### Step 3: Integrate Tailwind v4 & Setup shadcn/ui
* Install `@tailwindcss/vite` and `tailwindcss`.
* Run `npx shadcn@latest init` to setup config.
* Configure `vite.config.js` to load the Tailwind CSS plugin.

### Step 4: Write Custom Hooks
* `useChat.js`: Handles stream parsing using Fetch API `ReadableStream` reader to read incoming chunks of JSON and append to model messages.
* `useFetch.js`: Standard async fetch coordinator.

### Step 5: Build UI Components (Using shadcn/ui & Tailwind 4)
* **Sidebar Layout:** Modern dark-mode grid layout.
* **Dashboard Tab:** Render traditional search filters (seniority dropdowns, location tags) and `JobCard` list.
* **Analytics Tab:** Bar charts and area charts utilizing Recharts.
* **AI Chat Tab:** Chat bubbles with avatars, streaming text indicators, and error warnings.

### Step 6: Verify Quality
* Run `npm run format` to auto-format all code.
* Run `npm run lint` to assert zero linter violations.
* Run `npm run build` to verify clean build files.
