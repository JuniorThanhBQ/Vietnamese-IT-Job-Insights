# Third-party GitHub Actions used in workflows

This document lists the external actions called in workflows at [.github/workflows](../../.github/workflows), including the action name, the version pinned by SHA, and the primary purpose.

| Action | Version ID | Primary Purpose | Related Workflow |
| --- | --- | --- | --- |
| `actions/labeler` | `f27b608878404679385c85cfa523b85ccb86e213` | Automatically label pull requests based on changes in the repo | `auto-labeler-workflow.yml` |
| `agilepathway/label-checker` | `c3d16ad512e7cea5961df85ff2486bb774caf3c5` | Checks if PR labels match the allowed/disallowed list | `auto-labeler-workflow.yml` |
| `eps1lon/actions-label-merge-conflict` | `0273be72a0bbd58fcd71d0d6c02c209b50d1e5e1` | Apply the “conflicts” label to PRs when there are merge conflicts | `detect-conflicts.yml` |
| `tiangolo/latest-changes` | `c9b73efbc8992ef1a401e4235ea307a8ca8a724b` | Generate release notes / latest changes list from merged PRs | `latest-changes.yml` |
| `gitleaks/gitleaks-action` | `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` | Scan the repository and Git history to detect secrets and tokens | `security-code-workflow.yml` |
| `github/codeql-action/init` | `54f647b7e1bb85c95cddabcd46b0c578ec92bc1a` | Initialize CodeQL analysis for Python/JavaScript/TypeScript | `codeql.yml`, `security-code-workflow.yml` |
| `github/codeql-action/analyze` | `54f647b7e1bb85c95cddabcd46b0c578ec92bc1a` | Run CodeQL analysis and generate scan results | `codeql.yml`, `security-code-workflow.yml` |
| `github/codeql-action/upload-sarif` | `54f647b7e1bb85c95cddabcd46b0c578ec92bc1a` | Push SARIF reports to GitHub Code Scanning | `security-code-workflow.yml`, `security-containers-workflow.yml` |

> Note: Actions such as `actions/checkout`, `actions/setup-python`, `actions/setup-node`, and `actions/upload-artifact` are official GitHub actions and are therefore not listed here.
