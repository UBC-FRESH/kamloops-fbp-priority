# GitHub issue tree

Status: created and verified 2026-10-28; close-out queued 2026-10-29.

- Repository: https://github.com/UBC-FRESH/kamloops-fbp-priority (public since 2026-10-29)
- Documentation: https://ubc-fresh.github.io/kamloops-fbp-priority/
- Default branch: `main`
- Working branch: `feature/p0-bootstrap`
- Close-out pull request: #7
- Close-out report: `notes/reports/p0-closeout.md`
- Visibility, settings, and branch protection: unchanged from the repository defaults; no changes
  were made after creation.

## Authentication and pushes

`gh auth status` now succeeds. The device-flow attempt from the first session expired before
authorization; the maintainer authenticated separately, and the repository was created afterward.

The initial pushes were:

```bash
git push -u origin main
git push -u origin feature/p0-bootstrap
```

`main` contains the seed commit. `feature/p0-bootstrap` contains the Phase 0 work. No credentials or
tokens are recorded in the repository.

## Issue tree

| ID | Issue | Title | State |
| --- | --- | --- | --- |
| P0 | #1 | P0: Bootstrap and feasibility speed run | open, pr-open |
| P0.1 | #2 | P0.1: Adapt the agent contract, README, and roadmap | open, pr-open |
| P0.2 | #3 | P0.2: Fetch and audit the named datasets | open, pr-open |
| P0.3 | #4 | P0.3: Build the 100 m baseline FBP chain | open, pr-open |
| P0.4 | #5 | P0.4: Write the scope, scale, and shape map | open, pr-open |
| P0.5 | #6 | P0.5: Create the repository and Phase 0 issues | closed, complete |

All five child issues are linked to #1 as sub-issues. The issue bodies are kept in
`notes/scope/issues/` and were posted with `--body-file`.

## Verification

```bash
gh repo view UBC-FRESH/kamloops-fbp-priority --json visibility,defaultBranchRef,url
gh issue list --repo UBC-FRESH/kamloops-fbp-priority --state all
gh api repos/UBC-FRESH/kamloops-fbp-priority/issues/1/sub_issues \
  --jq '.[] | "#\(.number) \(.title)"'
```

## Creation record

The parent was created first, then the children, then each child was linked:

```bash
gh issue create --repo UBC-FRESH/kamloops-fbp-priority \
  --title "P0: Bootstrap and feasibility speed run" \
  --label phase --body-file notes/scope/issues/p0-parent.md

# parent=1; repeat for each child body with its title and the task label.
gh issue create --repo UBC-FRESH/kamloops-fbp-priority \
  --title "<child title>" --label task --body-file notes/scope/issues/<child body>

child_id=$(gh api repos/UBC-FRESH/kamloops-fbp-priority/issues/<child> --jq .id)
gh api -X POST repos/UBC-FRESH/kamloops-fbp-priority/issues/1/sub_issues \
  -F sub_issue_id="$child_id"
```

P0.5 closed after the activation comment. P0.1-P0.4 remain open until the Phase 0 close-out pull
request #7 is approved and merged. The close-out report is `notes/reports/p0-closeout.md`.
