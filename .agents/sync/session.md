# Session Handoff

- **Done:** Faster verification is built, reviewed by Antigravity, and merged to local `main`. Plan, rulings, and measurements: `docs/specs/2026-10-12-faster-verification-plan.md`.
- **How verification works now:**
  - `verify.test` is the fast suite. Browser tests go in `verify.e2e` and run only with `npm run verify:agent -- --e2e`: once per Tier 3 branch, before the review.
  - The commit hook skips the tests when the same content already passed `verify`.
  - A failure gets an Antigravity diagnosis only when it is over 150 lines, came from the e2e command, or left fresh browser artefacts. Otherwise read the excerpt.
  - Scout only when the files are unknown. Scout and diagnosis use `gemini-3.8-flash-low`; test writing and review use `gemini-3.8-flash-high`.
- **How Tier 3 works now:** design in chat, one `-plan.md` document, one approval, tasks grouped into few `builder` runs. Resuming a builder with SendMessage is much cheaper than starting a new one.
- **Measured:** this repo's suite 190 s to 56 s; the repeat run on commit 190 s to 1 s; scout 240 s to 93 s; diagnosis 22 s to 13 s. A review takes 6 to 10 minutes and 250,000 to 320,000 Antigravity tokens, and one timed out with nothing to show.
- **Open, needs the developer:**
  - No project has been started. Say what you are building.
  - `main` is not pushed to `origin`.
  - `npm run init:project` writes no `verify` commands, so a project started with the wizard keeps running this template's tests. `tailor-setup` sets them.
  - Deferred `tailor-setup` minors (dry-run omits the hook; skill present in both folders; backslash `source_spec`).
- **Not enforced, only written:** tier sizing, the builder hand-off, and when to run e2e.
- **Open these first:** `CLAUDE.md`, `README.md`, the plan named above.
