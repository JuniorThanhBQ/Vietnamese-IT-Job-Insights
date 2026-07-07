# SAST / Dependency / Secret Scanning Pipeline

This repo ships six independent workflows plus one shared composite action.
Independent workflows mean a flaky Semgrep run doesn't block CodeQL, each
has its own concise log, and each can be re-run individually from the
Actions tab.

| Workflow file | Tool | Scope | Trigger paths |
|---|---|---|---|
| `codeql.yml` | GitHub CodeQL | `backend/` (Python) + `frontend/` (JS/TS), matrix job per language | whole repo |
| `semgrep.yml` | Semgrep | whole repo | whole repo |
| `bandit.yml` | Bandit | `backend/` only | `backend/**` |
| `eslint-security.yml` | ESLint + `eslint-plugin-security` | `frontend/` only | `frontend/**` |
| `secret-scanning.yml` | Gitleaks | whole repo, full git history | whole repo, daily schedule |
| `osv-scanner.yml` | OSV-Scanner | `backend/` and `frontend/` dependency manifests, matrix job per target | whole repo |

All six run on `push`/`pull_request` to your main branches, on a schedule
(so a newly published CVE or ruleset update is caught even with no new
commits), and on `workflow_dispatch` for manual runs.

## Pass/fail and issue behavior

- Every tool is run in **fail-the-build mode** (`--error` for Semgrep,
  Bandit's own non-zero exit on findings at/above threshold, ESLint's
  default non-zero on lint errors, gitleaks' non-zero on a detected
  secret, OSV-Scanner's non-zero on a known vulnerability).
- **If every check passes, no issue is created** — the workflows simply go
  green.
- **If a job fails**, a final `notify-on-failure` job (`if: failure()`)
  runs the shared composite action at
  `.github/actions/report-security-issue/action.yml`, which:
  - Opens a new issue titled `[security] <check name> failed`, labeled
    **`security`**, linking to the failed run, ref, and commit.
  - If an open issue with that exact title already exists, it adds a
    comment instead of creating a duplicate — so a check that fails on
    every commit for a week doesn't produce seven issues.
  - Deliberately does **not** echo raw tool output, secret values, or
    exploit payloads into the issue body; it points back to the workflow
    run and, where applicable, the SARIF-backed Code Scanning alert.

All findings are also uploaded as SARIF via `github/codeql-action/upload-sarif`,
so alongside the created issue you get first-class annotations in the
**Security → Code scanning alerts** tab (line-level, dedup'd across runs,
dismissible with a reason).

## One-time setup

1. **Enable required features** (repo Settings → Code security and
   analysis):
   - Code scanning (needed for the SARIF uploads used by every workflow
     here).
   - Dependabot alerts (complements, but doesn't replace, OSV-Scanner).
   - Optionally enable GitHub's *native* secret scanning + push protection
     too — it's a repo setting, not a workflow, and works as a second,
     earlier line of defense (it can block a push before it ever reaches
     CI) alongside the `secret-scanning.yml` workflow here.
2. **Permissions**: each workflow already declares
   `permissions: contents: read, security-events: write, issues: write`
   at the workflow level — no repo-wide "read/write" default needed.
3. **Optional secret**: `SEMGREP_APP_TOKEN`, only if you want Semgrep AppSec
   Platform dashboards/PR comments. The workflow runs fine without it.
4. **Branch protection**: add these as required status checks on your
   default branch once they're green a few times:
   `CodeQL - python`, `CodeQL - javascript-typescript`,
   `Semgrep full-repo scan`, `Bandit static analysis`,
   `ESLint security scan`, `Gitleaks full-history scan`,
   `OSV-Scanner - backend`, `OSV-Scanner - frontend`.
5. **Frontend note**: `eslint-security.yml` assumes an ESLint 8-style
   `.eslintrc` setup (`--no-eslintrc` + `--config`). If `frontend/` is on
   ESLint 9 flat config, swap that step for an `eslint.config.security.mjs`
   that imports `eslint-plugin-security` and pass it via `--config`
   instead — flat config doesn't recognize `.eslintrc.json` overlays.
6. **Bandit noise control**: `bandit.yml` runs at `-ll -ii` (medium
   severity + medium confidence and above). If the first run is too noisy,
   either tighten to `-lll -iii` (high/high only) temporarily, or check in
   a `backend/.bandit` baseline config to permanently exclude accepted
   findings — don't lower this in response to a single failing PR.

## Versioning note

Action tags (`@v4`, `@v3`, `@v2`) and the OSV-Scanner download URL point at
the latest major version as of writing. Pin these to specific release tags
(or commit SHAs, for supply-chain hardening) when you adopt this, and
re-check the Marketplace pages for `github/codeql-action`,
`gitleaks/gitleaks-action`, and the OSV-Scanner releases page for the
current recommended usage before first run.


## Reminder: the security workflow above is created by claude.ai