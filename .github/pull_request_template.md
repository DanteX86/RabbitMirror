## Pull Request Title

feat(web): <short summary of change>

## Summary
- What does this PR change and why?
- Which issue(s) does it close? (e.g., Closes #123)

## Changes
- [ ] Feature: Web interface scaffolding and routes
- [ ] UI: Components and styles
- [ ] CLI/TUI integration (if applicable)
- [ ] Documentation updates (README/DEVELOPMENT)
- [ ] Tests added/updated

## Screenshots / Demos (if UI)
- Include key screenshots or a short demo GIF.

## How to Test
1) Checkout this branch:
   git checkout feature/web-interface
2) Install/update deps:
   make dev-setup
3) Start the app:
   - Next.js: make next-start (or NEXT_PORT=3001 make next-start)
   - CLI/TUI if relevant
4) Verify the following:
   - [ ] Routes render without errors
   - [ ] API integrations work
   - [ ] No console errors
   - [ ] Mobile/desktop responsiveness

## Backwards Compatibility
- [ ] No breaking changes
- [ ] Includes migration docs (if breaking)

## Quality Checklist
- [ ] make update passes (format, lint, quick tests)
- [ ] make ci (optional) passes locally
- [ ] Type hints where appropriate
- [ ] Security considerations reviewed

## Additional Notes
- Any known follow-ups or limitations.

