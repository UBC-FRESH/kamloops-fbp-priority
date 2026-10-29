Task identifier: P0.5
Parent phase issue: #1
Status: complete
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0), `notes/scope/github-issue-tree.md`

Goal:

Create the GitHub repository and the Phase 0 issue tree.

Scope:

- create `UBC-FRESH/kamloops-fbp-priority` as a private repository, later made public on 2026-10-29 to enable GitHub Pages;
- push `main` and `feature/p0-bootstrap`;
- create the P0 parent issue and five child issues, linked as sub-issues;
- activate Phase 0 in the roadmap and post the activation comment.

Out of scope:

- changing repository visibility, settings, or branch protection;
- tags or releases;
- any other repository.

Subtasks:

- [x] Authenticate `gh`.
- [x] Create the repository and push both branches.
- [x] Create the parent issue from `notes/scope/issues/p0-parent.md`.
- [x] Create the five child issues and link them as sub-issues.
- [x] Set the parent number and status in `ROADMAP.md`.
- [x] Post the activation comment and read it back.

Acceptance criteria:

- `gh repo view` shows a public repository with Pages enabled;
- `gh issue list` shows the parent and five children;
- the roadmap tracker matches the GitHub issue numbers;
- no repository setting or visibility change happens without a separate approval.

Verification:

```bash
gh auth status
gh repo view UBC-FRESH/kamloops-fbp-priority --json visibility,defaultBranchRef
gh issue list --repo UBC-FRESH/kamloops-fbp-priority --state open
```

Artifacts:

`notes/scope/github-issue-tree.md`, GitHub issue URLs.

Risks:

GitHub authentication was unavailable during the first session. It was resolved before the
repository was created; do not commit credentials. The repository was created private and made
public on 2026-10-29, with approval, to enable GitHub Pages. No branch-protection changes were made.

Completion metadata:

Added at closeout: merged in `eda7195` via pull request #7; dashboard green at `5e7602f`; CI run `40793125048` passed.
