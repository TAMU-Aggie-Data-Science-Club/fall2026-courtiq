# CourtIQ deliverable structure

This is the shared guide for creating assignments, dividing responsibilities and reviewing submissions. [DELIVERABLES.md](../DELIVERABLES.md) remains the semester roadmap; [ARCHITECTURE.md](../ARCHITECTURE.md) defines product requirements. **GitHub Issues are authoritative for actual owners, deadlines, status and approved changes.** Week 0 is an approved exception: Discord holds the deadline/updates and individual PRs into `deliverable0` record submissions and review. No Issue is required; the PM can link PRs to an Issue later. This document describes the process and proposed specialties, not a separate task tracker.

New to GitHub? Use [the GitHub walkthrough](../CONTRIBUTING.md#new-to-github): [PM Issue creation](../CONTRIBUTING.md#create-an-issue-pms), [member Issue use](../CONTRIBUTING.md#use-an-issue-members) and [PR submission](../CONTRIBUTING.md#open-a-pull-request-members).

## How a deliverable is created

The steps below apply to future Issue-based deliverables. For Week 0, publish the reviewed starter on `deliverable0`, announce the assignment/deadline in Discord and collect individual PRs; use [the PM release steps](../CONTRIBUTING.md#release-week-0-pms).

1. PMs choose a small, approved step toward a semester milestone. State what members should learn or implement and what is out of scope; do not add new features, data sources or dependencies implicitly.
2. Open the GitHub Issue with the goal, deadline, prerequisites, member/team assignments, file/output expectations, dependencies and a concrete acceptance checklist. Identify whether submission is individual or coordinated team work.
3. Prepare `issue-<n>/integration` using the established [contribution workflow](../CONTRIBUTING.md). Make the starter and any approved supporting files available there before members create feature branches.
4. Copy [assignment-template.md](assignment-template.md) into `weekly/weekN/`, add only the instructions and assets needed that week, and link its actual Issue. Update the [weekly index](README.md). Do not create future assignments before they are approved.
5. Give each member an explicit slice and reviewer in the Issue. For team work, agree on shared inputs/outputs and assign disjoint function bodies when members share a module, keeping shared imports/helpers PM-owned. If requirements change, record the decision in the Issue and update the instructions.

Each assignment should answer: **Who does what? What must it produce? What depends on it? How will it be checked? Where does the PR go?** Update the semester roadmap only when its milestones change; keep everyday task updates in Issues.

## Numbered teams and assignment ownership

Team numbers identify groups, not permanent specialties. Weekly Issues assign actual tasks; starter examples and support are available to everyone. Members propose ideas together and own clearly marked functions in the shared application modules. Names and TODO comments identify each member's section; Cemal handles integration conflicts. The [Week 1 guide](week1/week-01-player-team-prototypes.md) defines the current allocation.

### Leadership

**Ali — PM. Cemal Duman — U4 — Co-PM.** Prepare assignments, coordinate reviews, verify acceptance and support blocked members. For Week 1, Cemal handles feature merges, cross-PR conflicts and integration; members submit PRs, review peers and fix their own code. PMs own final integration-to-`main` review and merge decisions. No Technical Lead is appointed by this guide.

### Team 1

- Aiden Jackson
- Ignacio Wijatno
- Andrew Mok

### Team 2

- June Hwang
- Jason Q. Koffi
- Sri Abhinav Thatavarthi

### Team 3

- Michael Du
- Casey Hawkings
- Jack Dunlap

### Shared boundaries

Collect only from approved sources; preserve IDs, units, periods and provenance; keep datasets under ignored `data/`. Collection, calculations, charts and UI have separate responsibilities per ARCHITECTURE. Shared inputs/outputs allow independent development; assignments identify who consumes each result. Database/schema work requires an explicit task. ML stays stretch work. Week 1's shared examples are development aids, not actual NBA results.

## What each member is assigned for Week 0

All members complete **the same individual [onboarding assignment](week0/week-00-onboarding.md)**. Team specialties do not change this week's task:

- Set up local Python 3.12 and pass environment verification.
- Complete [Docker/PostgreSQL setup](../docs/SETUP.md), show a healthy service, run `SELECT 1;` and stop it safely with persistent storage intact.
- Copy `weekly/week0/onboarding.py` to `weekly/week0/<github-handle>_onboarding.py`.
- Complete the inspection, minimum-games filter, scoring rank and Plotly chart TODOs using API or synthetic backup data.
- Submit your personal script through an individual PR and briefly summarize the verification results in its description. No screenshots or attachments are required for Week 0.

There is no required proposal, notebook, database schema/ingestion or editor for Week 0. Docker runs PostgreSQL only; Python stays local. Future Issues specify the exact member/team implementation tasks; the suggested focus above is not an automatic future assignment.

## What the Co-PM checks

Cemal or the designated reviewer checks the assignment's acceptance criteria (the Week 0 checklist, or the Issue for future tasks) against the actual diff and reproducible output. For Week 0, review the submitted script, run it, and read the member's verification summary; screenshots are not required.

| Check | What must be verified |
| --- | --- |
| Assignment coverage | Every required task/artifact is present; the PR stays within scope and identifies its owner(s) |
| Execution | The documented command or relevant checks run in the shared environment; paths and imports work |
| Correctness | Calculations match definitions and units; relevant edge cases and important results have meaningful checks |
| Data and charts | Source, season/period and axes are clear; synthetic data is labeled; missing/failing data is handled appropriately |
| Collaboration | Agreed team inputs/outputs match; each member's contribution is identifiable; integration does not break existing features |
| Submission | PR targets the correct integration branch, summarizes verification results and links its Issue when one exists; review feedback is addressed |
| Repository hygiene | No real datasets, environments, generated caches or credentials; no unapproved dependency/source/scope changes |

**Week 0 specifically:** confirm Python verification, healthy Docker/PostgreSQL and the reported successful `SELECT 1;` result; confirm the member can stop/restart without deleting data and has not submitted `.env` or volume files. Then run the member script; confirm `GP >= 20` includes the boundary; verify the top five uses descending `PTS_PER_GAME`; check the chart matches those rows and identifies API/backup correctly; confirm only the member script is submitted. API failure with a clearly labeled working backup is acceptable. Shared starter/backup files should remain unchanged.

If something is incomplete, request specific changes and recheck the affected behavior after the member updates the PR. Do not mark the Issue complete merely because its deadline passed.

## How work is submitted

- **Individual work:** each member uses `issue-<n>/<member-slice>` and the function/file slice specified by the assignment. Week 1 uses named TODO functions in shared `src/` modules; only the personal brainstorming document has an individual filename. Week 0 uses `deliverable0-<github-handle>` and one member script, with the PR targeting `deliverable0`.
- **Team work:** split the Issue into small member-owned feature slices. Each slice has its own feature branch/PR into the same Issue integration branch. A slice can be one named function in a shared app module; members change only their own section. Name the contributor(s), handoff and reviewer in the Issue/PR; do not hide all work in one indistinguishable submission. A pair-owned slice is acceptable when explicitly assigned.
- **PR contents:** explain what changed, link the Issue when one exists, give the relevant verification commands and briefly summarize their results. Week 0 requires no screenshots or attachments. Stage only the assigned source files; generated chart/data outputs stay local.
- **Shared Issues:** use `Related to #<n>` so one member's submission does not close the whole team assignment. Reserve closing the Issue for completion of all required slices and the PM's final review.
- **Review and merge:** request a teammate/Co-PM review and address any configured automated-review feedback. Typically, Cemal performs feature → integration merges and handles cross-PR conflicts; members do not merge or rebase branches. Other assignments follow their approved merge ownership. PMs review integration → `main` when all required work is collected and verified. For Week 0, `deliverable0` is that shared integration branch.

For future tasks the actual Issue number is supplied by the PM; `<n>` is a placeholder. Week 0 needs no Issue number; members share PR links and blockers in Discord. Follow CONTRIBUTING for worktree, synchronization, commit/push and cleanup commands. Members submit PRs; they do not push directly to `main`.
