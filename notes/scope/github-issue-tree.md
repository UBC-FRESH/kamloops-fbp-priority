# GitHub issue tree: offline manifest

Status: blocked on authentication. Nothing has been created or pushed to GitHub.

## What was attempted

- `gh --version` initially failed: `gh` was not installed. It is now installed at
  `~/.local/bin/gh` (v2.103.3).
- `gh auth status` reports: `You are not logged into any GitHub hosts.`
- There is no `GITHUB_TOKEN` in the environment, no `~/.ssh` key, and no git credential helper.
- The local repository is initialized on `main` with the seed commit `40f43bb`, and the Phase 0 work
  is on `feature/p0-bootstrap`. The working tree has not been pushed.

## Intended repository

- Owner: `UBC-FRESH`
- Name: `kamloops-fbp-priority`
- Visibility: private
- Default branch: `main`

## Commands after authentication

Run these only after `gh auth status` succeeds and the maintainer confirms the repository name and
owner.

```bash
cd kamloops-fbp-priority
gh auth status
gh repo create UBC-FRESH/kamloops-fbp-priority --private --source=. --remote=origin
git push -u origin main
git push -u origin feature/p0-bootstrap
gh repo edit UBC-FRESH/kamloops-fbp-priority --default-branch main
```

Then create the Phase 0 parent issue and its child issues. Write bodies to files and post them with
`--body-file`; never build them from escaped strings.

```bash
gh issue create \
  --repo UBC-FRESH/kamloops-fbp-priority \
  --title "P0: Bootstrap and feasibility speed run" \
  --label phase \
  --body-file notes/scope/issues/p0-parent.md
```

Read the parent issue number, then create the children and link each as a sub-issue:

```bash
parent=7   # replace with the real parent issue number
for body in notes/scope/issues/p0-*.md; do
  title=$(head -1 "$body")
  gh issue create --repo UBC-FRESH/kamloops-fbp-priority \
    --title "$title" --label task --body-file "$body"
done
```

GitHub's sub-issue API link:

```bash
child_id=$(gh api repos/UBC-FRESH/kamloops-fbp-priority/issues/CHILD --jq .id)
gh api -X POST repos/UBC-FRESH/kamloops-fbp-priority/issues/PARENT/sub_issues \
  -F sub_issue_id="$child_id"
```

Then set the parent number and status in `ROADMAP.md` and the tracker map, create the Phase 0 branch
from `main` (it already exists locally), and post the activation comment.

## Issue titles

| ID | Title | Body |
| --- | --- | --- |
| P0 | `P0: Bootstrap and feasibility speed run` | `notes/scope/issues/p0-parent.md` |
| P0.1 | `P0.1: Adapt the agent contract, README, and roadmap` | `notes/scope/issues/p0-1-contract.md` |
| P0.2 | `P0.2: Fetch and audit the named datasets` | `notes/scope/issues/p0-2-data-audit.md` |
| P0.3 | `P0.3: Build the 100 m baseline FBP chain` | `notes/scope/issues/p0-3-baseline-fbp.md` |
| P0.4 | `P0.4: Write the scope, scale, and shape map` | `notes/scope/issues/p0-4-mental-map.md` |
| P0.5 | `P0.5: Create the private repository and Phase 0 issues` | `notes/scope/issues/p0-5-github.md` |

The child bodies are written from the seed's task template. Fill in the real parent number and the
commit hashes at closeout. The roadmap and changelog remain the source of truth until the issues
exist.
