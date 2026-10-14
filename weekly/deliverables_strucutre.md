# CourtIQ deliverable structure

This is the shared guide for creating assignments, dividing responsibilities and reviewing submissions. [DELIVERABLES.md](../DELIVERABLES.md) remains the semester roadmap; [ARCHITECTURE.md](../ARCHITECTURE.md) defines product requirements. **GitHub Issues are authoritative for actual owners, deadlines, status and approved changes.** Week 0 is an approved exception: Discord holds the deadline/updates and individual PRs into `deliverable0` record submissions and review. No Issue is required; the PM can link PRs to an Issue later. This document describes the process and proposed specialties, not a separate task tracker.

New to GitHub? Use [the beginner walkthrough](../CONTRIBUTING.md#new-to-github): [PM Issue creation](../CONTRIBUTING.md#create-an-issue-pms), [member Issue use](../CONTRIBUTING.md#use-an-issue-members) and [PR submission](../CONTRIBUTING.md#open-a-pull-request-members).

## How a deliverable is created

The steps below apply to future Issue-based deliverables. For Week 0, publish the reviewed starter on `deliverable0`, announce the assignment/deadline in Discord and collect individual PRs; use [the PM release steps](../CONTRIBUTING.md#release-week-0-pms).

1. PMs choose a small, approved step toward a semester milestone. State what members should learn or implement and what is out of scope; do not add new features, data sources or dependencies implicitly.
2. Open the GitHub Issue with the goal, deadline, prerequisites, member/team assignments, file/output expectations, dependencies and a concrete acceptance checklist. Identify whether submission is individual or coordinated team work.
3. Prepare `issue-<n>/integration` using the established [contribution workflow](../CONTRIBUTING.md). Make the starter and any approved supporting files available there before members create feature branches.
4. Copy [assignment-template.md](assignment-template.md) into `weekly/weekN/`, add only the instructions and assets needed that week, and link its actual Issue. Update the [weekly index](README.md). Do not create future assignments before they are approved.
5. Give each member an explicit slice and reviewer in the Issue. For team work, agree on shared inputs/outputs and avoid assigning the same file to two people simultaneously. If requirements change, record the decision in the Issue and update the instructions.

Each assignment should answer: **Who does what? What must it produce? What depends on it? How will it be checked? Where does the PR go?** Update the semester roadmap only when its milestones change; keep everyday task updates in Issues.

## Proposed teams — specialization when the time comes

### Leadership

**Cemal Duman — U4 — Co-PM.** Work with the PM to prepare clear Issues, confirm prerequisites, coordinate reviews, check acceptance evidence and bring blockers/scope decisions to the PMs. PMs own the final integration-to-`main` review and merge decision.

The roster below replaces earlier proposed member groupings. Suggested focus describes how members can contribute once specialization starts; actual weekly tasks are assigned in GitHub Issues. Experience levels guide support, not grading or permission to participate. Teams remain together and can rotate technical responsibilities as needed.

### Team A — Data and Architecture

| Member | Year | Experience | Suggested focus when assigned |
| --- | --- | --- | --- |
| Aiden Jackson | U3 | Advanced | Coordinate data collection/validation slices and help teammates debug |
| Ignacio Wijatno | U2 | Beginner | Implement a small approved fetch/cleaning task with guidance |
| Andrew Mok | U4 | Novice | Implement an assigned data-organization or schema slice with review |

**Team requirements when the relevant Issue is approved:** collect player/team/game data from approved sources; keep IDs, seasons and units consistent; clean and validate tables; document fields and provenance in the appropriate project files; keep downloads/caches under ignored `data/`. Handle request failures and avoid unnecessary repeated requests. Implement the planned PostgreSQL work only when it is explicitly assigned—Week 0 requires the PostgreSQL environment check, but no schema or ingestion implementation.

**Handoff:** provide reproducible loading/cleaning code and agreed tables to Teams B/C. Confirm data definitions with Team C before committing to a schema. This supports the data-foundation and integration milestones.

### Team B — Application and Visualization

| Member | Year | Experience | Suggested focus when assigned |
| --- | --- | --- | --- |
| June Hwang | U1 | Intermediate | Coordinate page layouts and chart integration; support teammates |
| Jack Dunlap | U2 | Beginner–Intermediate | Implement an assigned interaction, filter or page slice |
| Jason Q. Koffi | U1 | Beginner | Implement a small page/chart component and empty-state handling with guidance |

**Team requirements when the relevant Issue is approved:** implement Streamlit interactions and Plotly views for Players, Teams, Compare and Trends, following the assigned scope in ARCHITECTURE. Label metrics, periods and sources clearly; handle missing/stale data; reuse validated analytics rather than duplicate formulas in the UI. Keep the app runnable as reviewed slices are integrated.

**Handoff:** consume Team A's agreed data and Team C's calculations, then provide an interactive view with execution evidence. This supports the profile, comparison/trend and integration milestones.

### Team C — Statistics and Analytics

| Member | Year | Experience | Suggested focus when assigned |
| --- | --- | --- | --- |
| Michael Du | U4 | Advanced | Coordinate formulas and validation; help teammates reason about results |
| Casey Hawkings | U4 | Intermediate | Implement assigned comparison or recent-performance calculations |
| Sri Abhinav Thatavarthi | U1 | Beginner | Implement a small metric/filter/checking task with guidance |

**Team requirements when the relevant Issue is approved:** implement documented player/team metrics, fair comparisons, league percentiles and recent-performance calculations. Define eligibility, normalization, periods and missing-data handling; distinguish totals from averages; validate important calculations independently. Trend explanations must not turn ordinary variation into unsupported claims. Forecasting/ML remains stretch work requiring approval.

**Handoff:** provide reusable calculations and clear definitions to Team B; agree on required inputs with Team A. This supports the profile, comparison and trend milestones.

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

- **Individual work:** each member uses `issue-<n>/<member-slice>` and unique filenames specified by the assignment. Week 0 uses `deliverable0-<github-handle>` and one member script, with the PR targeting `deliverable0`.
- **Team work:** split the Issue into small member-owned feature slices. Each slice has its own feature branch/PR into the same Issue integration branch. Name the contributor(s), handoff and reviewer in the Issue/PR; do not hide all work in one indistinguishable submission. A pair-owned slice is acceptable when explicitly assigned.
- **PR contents:** explain what changed, link the Issue when one exists, give the relevant verification commands and briefly summarize their results. Week 0 requires no screenshots or attachments. Stage only the assigned source files; generated chart/data outputs stay local.
- **Shared Issues:** use `Related to #<n>` so one member's submission does not close the whole team assignment. Reserve closing the Issue for completion of all required slices and the PM's final review.
- **Review and merge:** request a teammate/Co-PM review, address any configured automated-review feedback, and merge feature → integration only after approval. PMs review integration → `main` when all required work is collected and verified. For Week 0, `deliverable0` is that shared integration branch.

For future tasks the actual Issue number is supplied by the PM; `<n>` is a placeholder. Week 0 needs no Issue number; members share PR links and blockers in Discord. Follow CONTRIBUTING for worktree, synchronization, commit/push and cleanup commands. Members submit PRs; they do not push directly to `main`.
