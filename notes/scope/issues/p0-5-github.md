Task identifier: P0.5
Parent phase issue: #TBD
Status: planned
Branch: `feature/p0-bootstrap`
Related planning: `ROADMAP.md` (Phase 0), `notes/scope/github-issue-tree.md`

Goal:

Create the private GitHub repository and the Phase 0 issue tree.

Scope:

- create `UBC-FRESH/kamloops-fbp-priority` as a private repository;
- push `main` and `feature/p0-bootstrap`;
- create the P0 parent issue and five child issues, linked as sub-issues;
- activate Phase 0 in the roadmap and post the activation comment.

Out of scope:

- changing repository visibility, settings, or branch protection;
- tags or releases;
- any other repository.

Subtasks:

- [ ] Authenticate `gh`.
- [ ] Create the private repository and push both branches.
- [ ] Create the parent issue from `notes/scope/issues/p0-parent.md`.
- [ ] Create the five child issues and link them as sub-issues.
- [ ] Set the parent number and status in `ROADMAP.md`.
- [ ] Post the activation comment and read it back.

Acceptance criteria:

- `gh repo view` shows a private repository;
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

The environment has no GitHub credentials. Do not fake the GitHub side; keep the manifest current
until authentication is available.
