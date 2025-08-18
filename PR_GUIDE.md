# Pull Request Guide

This repository uses GitHub Pull Requests (PRs) for code review.

## Open a PR from feature/web-interface to main

1. Ensure your local branch is pushed:
   ```bash
   git checkout feature/web-interface
   git push -u origin feature/web-interface
   ```

2. Open a PR on GitHub (browser):
   - Go to your repo: https://github.com/DanteX86/RabbitMirror
   - Click "Compare & pull request"
   - Base: `main`, Compare: `feature/web-interface`
   - The PR description will auto-fill from .github/pull_request_template.md

3. Fill in details and submit the PR.

## Local checklist before opening the PR

- [ ] Sync with latest main:
  ```bash
  git fetch origin
  git rebase origin/main
  # or merge if preferred:
  # git merge origin/main
  ```
- [ ] Run maintenance:
  ```bash
  make update
  # If lint errors are intentional, document rationale in the PR
  ```
- [ ] Run full CI locally (optional):
  ```bash
  make ci
  ```

## After opening the PR

- Ensure CI passes on GitHub Actions
- Request review from maintainers
- Address review comments with additional commits

## Merging

- Use squash merge unless the branch has meaningful, reviewable commits
- Delete the feature branch after merge if no longer needed

