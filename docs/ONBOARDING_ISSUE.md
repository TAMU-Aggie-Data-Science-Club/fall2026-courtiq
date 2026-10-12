# Proposed issue: Deliverable 0 — Technical Onboarding & Product Exploration

**Draft only — not published.** PM: set the exact deadline and issue number, then create the issue's integration branch with the reviewed starter before inviting members. Do not use the local `issue-pending/onboarding-setup` preview namespace for student submissions.

## Goal

Prepare all nine CourtIQ members for our first design meeting through an individual 1–2 hour assignment: a working Python 3.12 environment, guided exploration of fictional NBA-style data, and one feature/design proposal per person. Research proposals are discussion inputs, not approved additions to product scope.

## Deadline and resources

- Due: **PM to set date/time before first meeting (America/Chicago)**.
- Assignment: [weekly/week-00-onboarding.md](../weekly/week-00-onboarding.md) (complete assignment and setup); [initial PDF snapshot](DELIVERABLE_0.pdf).
- Setup: [docs/SETUP.md](SETUP.md).
- Starter: [notebooks/00_onboarding.ipynb](../notebooks/00_onboarding.ipynb).
- Product plan: [ARCHITECTURE.md](../ARCHITECTURE.md).
- Contribution rules: [CONTRIBUTING.md](../CONTRIBUTING.md).

When pasting this text into GitHub, replace the relative links above with repository URLs pointing to the assigned integration branch (or main after the starter is reviewed and merged). Fill in the actual issue number wherever `<n>` appears.

This issue is authoritative for owners, task status, deadlines and approved changes. The [weekly index](../weekly/README.md) and assignment document provide instructions; record changes here and update the assignment when needed.

## Member instructions

Comment with your username and team to claim your individual slice. Branch from the shared `issue-<n>/integration` using `issue-<n>/onboarding-<github-handle>`. Save your notebook as `notebooks/submissions/<github-handle>_00_onboarding.ipynb` and proposal as `docs/proposals/<github-handle>.md`. Follow the assignment's worktree and environment commands. Keep the common starter and fixture unchanged.

Open one PR into **`issue-<n>/integration`**, title `Deliverable 0: Your Name`, and say `Related to #<n>` rather than closing the shared issue. Attach successful verification and chart execution evidence, identify your OS/Python/kernel, and request a teammate's or PM's review. Respond to feedback with follow-up commits. Only the PM handles the final integration-to-main review.

## Acceptance criteria per member

- [ ] Python 3.12, activated `.venv`, package verifier PASS and `pip check`.
- [ ] Correct Jupyter kernel; saved notebook executes from a fresh kernel without live API access.
- [ ] All inspection TODOs answered, with totals/per-game units explained.
- [ ] At least 20 games filter includes the boundary and excludes low-game rows.
- [ ] Top five use descending points per game; Plotly chart matches rows, values and ordering.
- [ ] Synthetic title/labels; short interpretation with sample-size and metric limitations.
- [ ] One proposal answers all template questions and includes an example/sketch.
- [ ] Unique paths, evidence and correct integration-base PR; shared starter unchanged.
- [ ] No real datasets, secrets, venvs or generated caches in the submission.
- [ ] Human review complete; any configured automated-review feedback addressed.

## Team completion tracker

Check a member only after their PR meets the criteria and is approved/merged into integration. Replace `PR: TBD` with the member's PR link.

- [ ] Team A — Aiden Jackson — PR: TBD
- [ ] Team A — Ignacio Wijatno — PR: TBD
- [ ] Team A — Andrew Mok — PR: TBD
- [ ] Team B — June Hwang — PR: TBD
- [ ] Team B — Jason Q. Koffi — PR: TBD
- [ ] Team B — Sri Abhinav Thatavarthi — PR: TBD
- [ ] Team C — Michael Du — PR: TBD
- [ ] Team C — Casey Hawkings — PR: TBD
- [ ] Team C — Jack Dunlap — PR: TBD

Team A researches data/endpoints/organization, Team B layouts/interactions/visualizations, and Team C metrics/comparisons/percentiles/recent form. Teams remain together and rotate technical responsibilities later.

## PM completion

- [ ] Deadline and numbered integration branch announced; starter available.
- [ ] All nine submissions reviewed and collected into integration.
- [ ] Proposals summarized for first meeting; implementation/data-source scope decisions recorded separately.
- [ ] PM reviews integration → main through the established process, then closes this issue.
