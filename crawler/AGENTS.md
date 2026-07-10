# Crawler Agent Specifications

This document defines the roles, constraints, coding guidelines, and quality standards for AI Agents working inside the `crawler/` directory.

---

## 1. Role & Scope
The crawler package is designed to periodically fetch, parse, and normalize Vietnamese Software Engineer job descriptions (JDs) from targeted portals (primarily **ITviec** and **TopDev**) and load them into the database.

---

## 2. Architecture & File Organization
All crawler code must be organized into clear modular layers:
* **`base/`:** Handles browser automation logic (`BaseCrawler`). This is the only module interacting with Playwright.
* **`parser/`:** Selectolax parsing wrappers (e.g., `ITViecParser`, `TopDevParser`). They MUST accept only HTML strings and operate strictly without network or database IO.
* **`pipelines/`:** Orchestrator layer (`JobPipeline`) that connects fetching, parser selection, metadata normalization, and DB upserts.
* **`utils/`:** Helper utilities including normalizers (`normalizer.py` for salaries, seniority levels, remote policies, and contract types).

---

## 3. Low-Resource & Anti-Detection Constraints (ADR-03 Compliance)
To run reliably under Windows 11 with 8GB RAM and i7 Gen 4 CPU:
1. **Parallel Tabs Limit:** Concurrency must be capped at a maximum of **2 parallel tabs** using an internal asyncio semaphore.
2. **Asset Blocking:** Intercept requests to abort downloading heavy assets: `image`, `font`, `media`, and `stylesheet` (except when visual debugging is required).
3. **Engine Memory Caps:** Launch Playwright Chromium with V8 flags: `--js-flags=--max-old-space-size=512` to limit node process memory growth.
4. **Delays & Rotation:** Mimic human browsing with random delays (1.0 to 3.0s) between requests and rotate User-Agent strings.

---

## 4. Coding Standards & Lints
* **Python Compatibility:** Python >= 3.12.
* **Linter Standards:**
  * All crawler code must score **10.00/10** on `pylint` runs.
  * Use the settings defined in `backend/pyproject.toml` (e.g., `pylint --rcfile=backend/pyproject.toml crawler/`).
* **Commenting Rule:**
  * **No Indiscriminate Commenting:** Avoid comments that simply restate what the code does.
  * Only comment when explaining complex anti-scraping bypasses, parsing heuristics, or structural workarounds.
* **Privacy & Relative Paths:** Never write absolute local file paths (e.g. starting with drive letters like `C:/` or system username directories). All referenced links must be relative to the repository root.
