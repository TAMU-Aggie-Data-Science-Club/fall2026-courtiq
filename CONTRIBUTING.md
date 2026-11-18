# Contributing Guide

This guide explains how the Aggie Data Science Club team uses GitHub, including the first steps for people who have never used Issues, commits or pull requests.

**New to GitHub?** Start with [the terms and walkthrough below](#new-to-github). For Week 0, PMs use [the release steps](#release-week-0-pms) and members follow [the assignment](weekly/week0/week-00-onboarding.md) and [PR walkthrough](#open-a-pull-request-members). The Issue guides below apply to future tasks. Then read your role's section, [The Flow](#the-flow-issue--main) and [Staying in Sync](#staying-in-sync).

> **Two roles, one repo.** **Project Managers (PMs)** are *managers*: they turn goals into issues, review pull requests, and are the only people who approve merges to `main`. **Members** are *developers*: they take an issue, build it on a branch, open a pull request, respond to review, and merge their work up the tree. If you are an AI agent working in this repo, also read [`AGENTS.md`](AGENTS.md) — it is the strict machine-facing version of this same workflow.

> **Companion files.** This guide links to other template files — [`AGENTS.md`](AGENTS.md), [`README.md`](README.md), [`DELIVERABLES.md`](DELIVERABLES.md), [`DATA.md`](DATA.md), and the [`data/`](data/) folder. They are part of the template and are populated as the repo is set up (each lands through its own issue and PR, exactly as described below). If a link 404s, that file simply hasn't been merged to `main` yet — it will be before the template is complete.

**First assignment:** follow [Week 00](weekly/week0/week-00-onboarding.md). Week 0 is the PM-approved exception to the Issue requirement: each member submits their own Python script through a feature PR into `deliverable0`, with deadline/help in Discord. Future work follows the Issue-based workflow below.

**Week 1:** follow [NBA data and visual prototypes](weekly/week1/week-01-player-team-prototypes.md). Members submit their named TODO function in a shared app module plus a personal brainstorming document; Cemal coordinates reviews and performs feature-to-integration merges/conflict resolution. This assignment-specific ownership overrides member merge/cleanup steps below; PMs retain final review into `main`.

---

## Table of Contents

1. [New to GitHub](#new-to-github)
2. [The mental model](#the-mental-model)
3. [The flow: issue → `main`](#the-flow-issue--main)
4. [Staying in sync](#staying-in-sync)
5. [For Members (developers)](#for-members-developers)
6. [For Project Managers (managers)](#for-project-managers-managers)
7. [Branch naming](#branch-naming)
8. [Worktrees: one issue, one tree](#worktrees-one-issue-one-tree)
9. [Git commands in context](#git-commands-in-context)
10. [Code-review agents (strongly recommended)](#code-review-agents-strongly-recommended)
11. [Golden rules](#golden-rules)

---

## New to GitHub

Use the website for Issues and PRs, and a terminal (PowerShell on Windows, Terminal on macOS/Linux) for Git commands. An editor is only needed to change your Python file; no particular editor or GitHub CLI installation is required.

| Term | Meaning in this project |
| --- | --- |
| Repository / repo | The project's files and their saved change history |
| Git / GitHub | Git manages changes on your computer; GitHub hosts the shared repository online |
| Issue | A task card: instructions link, deadline, owners, questions and completion checklist |
| Clone | Download a local working copy and its Git history |
| Branch | A named line of work; your feature branch keeps your work separate until reviewed |
| Integration branch | The shared branch collecting approved work for an assignment; `deliverable0` for Week 0 |
| Worktree | Another local folder for a branch, backed by the same clone |
| Stage / commit | Choose the files for your next saved change, then save that change locally |
| Push / fetch | Upload committed changes to GitHub / download knowledge of remote branches and commits |
| Pull request / PR | A request for teammates to review and merge your branch's changes |
| Base / compare | A PR's destination branch / the branch containing your changes |
| Merge | Bring reviewed changes into the destination branch |

An assignment file explains the work, an Issue tracks it, and a PR contains the finished code. **Week 0 has individual PRs into `deliverable0`, with no Issue required.** Future tasks use Issues; PMs choose their breakdown. The number `42` in examples below is a placeholder: use the number shown on your real Issue.

### Create an Issue (PMs)

This is for future Issue-based work; Week 0 uses [the release steps](#release-week-0-pms).

1. Sign into GitHub and open [the CourtIQ repository](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq).
2. Select **Issues → New issue**. Choose the appropriate template or the blank-Issue option.
3. Enter a clear task title and description with the goal, deadline, instructions link, owner(s), expected files/output and acceptance checklist.
4. Use **Assignees** to identify responsible members, if available. For shared tasks, keep a member completion checklist and have members claim their slices. Add relevant labels/Project tracking as needed.
5. Submit the Issue. GitHub supplies its number, shown beside the title and at the end of its URL. Copy that actual number and URL; `42` in this guide is an example only.
6. Prepare the matching integration branch and publish any reviewed starter files through the workflow in [the PM section](#for-project-managers-managers). An Issue does not upload local code.
7. Link the published instructions and announce the actual Issue URL, deadline and integration branch. Edit the Issue description to record changes and completion; comments collect questions, blockers and PR links. Close it only after all required slices and final review are complete.

[GitHub's Issue creation reference](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue).

### Use an Issue (members)

This is for future tasks. Week 0 members follow [the assignment](weekly/week0/week-00-onboarding.md) and use Discord for questions/PR links.

1. Open the Issue URL sent by the PM, or find it in the repository's **Issues** tab.
2. Read its description, linked instructions and comments. Note the actual number, deadline and integration branch; do not copy example `42` unless it is real.
3. Confirm your assignment/claim in a comment with your name, GitHub username, team and slice. For shared tasks, claim only your slice.
4. Follow its feature-branch/worktree instructions and complete your assigned work. Use your feature worktree rather than editing the shared integration or `main` checkout.
5. If blocked, comment with the command, error and OS, with credentials removed. Ask before changing scope or the agreed workflow.
6. Post your PR link in an Issue comment. PMs update completion after review; closing the Issue is not how you submit.

### Open a pull request (members)

First save your files, run the assignment checks, stage only your own source files, commit them and push your feature branch. [Week 0](weekly/week0/week-00-onboarding.md#4-submit-your-script) provides the exact commands and explains them.

1. In the GitHub repo, select **Pull requests** → **New pull request**.
2. For Week 0, set **base** to `deliverable0` and **compare** to `deliverable0-<your-github-handle>`. For future tasks, use **base** `issue-<n>/integration` and **compare** `issue-<n>/<slice>`. This means “send my feature changes to the shared assignment branch.”
3. Inspect the changed files. Week 0 should show only your `weekly/week0/<handle>_onboarding.py`, not the common starter, backup, environments or generated chart. If you see unrelated work, stop and ask the PM before creating the PR.
4. Select **Create pull request**, give it a clear title, and describe what you changed and how you ran/checked it. For Week 0, include your name/team, source choice, Python verifier and Docker health/SQL results; no Issue reference is required. Week 0 requires no screenshots or file attachments; a brief text verification summary is sufficient. Future tasks specify their own submission requirements.
5. Submit the PR. In its **Reviewers** area, select a teammate or PM/Co-PM. If you cannot choose a reviewer, share the PR link in Discord for Week 0 (or its Issue for future tasks) and ask a PM to arrange review.
6. Read comments on the PR's **Conversation** and **Files changed** tabs. Edit the same local files on the same feature branch, rerun relevant checks, then commit and push the fixes. The existing PR updates automatically; there is no need to open another PR for that feedback.
7. Reply to review comments, explain your change and request another review. Wait for human approval and any configured automated checks. Merge up only under the project's rules; PMs handle the final integration-to-`main` PR.

Use `Related to #<n>` on individual submissions for a shared Issue; a closing keyword on one member's PR would misrepresent the remaining work. [GitHub's PR creation reference](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request).

---

## The mental model

Future tasks start as a **GitHub Issue** (the *why*) and end as a **merge into `main`** (the *done*). Week 0 starts from the published assignment and Discord announcement; `deliverable0` collects its reviewed feature PRs before PM review into `main`. In between, work lives on branches organized as a small **tree**:

```
main                         ← protected. Only PMs merge here.
 └── issue-42/integration    ← one "root" branch per issue (the trunk of this issue's tree)
      ├── issue-42/loader     ← a feature branch: one cohesive piece of the issue
      └── issue-42/charts      ← another feature branch, worked in parallel
```

- **`main`** is the source of truth. It should always be in a known-good state. Nobody pushes to it directly.
- **An integration (root) branch** is created per issue. It collects all the work for that issue and is the **only** branch that opens a pull request into `main`.
- **Feature branches** hang off the integration branch. Each is one small, reviewable slice. They merge *up* into the integration branch, not into `main`.

Work flows **up the tree**: feature → integration → `main`. Reviews happen at every step. When `main` finally receives the integration branch, the whole team is back on the same page.

---

## The flow: issue → `main`

This is the workflow for publishing project changes. Week 0 follows the same review/merge direction through `deliverable0`, skipping the Issue steps as explicitly approved by the PM.

1. **Open an Issue.** Describe the problem, the goal, and a checklist of acceptance criteria. This prerequisite applies to future work; Week 0 uses its published assignment/Discord announcement.
2. **Cut the tree.** From the latest `main`, create the issue's integration branch, then a feature branch (in its own worktree) for the slice you're building.
3. **Build the slice.** Small, focused commits. Push early so others can see progress.
4. **Open a Pull Request** from your feature branch into the **integration branch** (not `main`).
5. **Review.** Wait for the code-review agent (if enabled) and for a human reviewer. Address the comments.
6. **Merge up.** Once approved, merge the feature branch into the integration branch. Repeat 2–6 for each slice.
7. **PM reviews the integration branch → `main`.** When every slice for the issue has merged into the integration branch, a PM does the final review and merges to `main`.
8. **Clean up.** Delete merged branches (local + remote) and remove the worktree. **History is preserved by the merge commits** — deleting the branch label does not delete the commits.
9. **Close the Issue** (a merged PR that says `Closes #42` does this automatically).

---

## Staying in sync

**Week 1:** start from the PM-published `issue-11/integration` branch using the assignment's worktree commands. Cemal handles branch synchronization and merge conflicts; members keep working on their feature branches. The general `main`/rebase guidance below does not override that assignment.

**This is the most common source of pain, so do it reflexively.** GitHub is the source of truth, not your laptop. Before you start any work — and regularly while you work — pull the latest:

```sh
git switch main
git pull origin main          # fast-forward your local main to match GitHub
```

When you cut a new branch, cut it from an **up-to-date** `main`. If your feature branch has fallen behind the integration branch while you were building, bring it forward before opening/updating your PR (see [rebase vs. merge](#git-commands-in-context)).

If you skip this, you will build on stale code and hit avoidable merge conflicts. **When in doubt, `git fetch` and look before you leap:**

```sh
git fetch origin              # update your view of every remote branch (changes nothing local)
git status                    # are you ahead/behind? clean/dirty?
```

---

## For Members (developers)

You own the *building*. Your job is to turn one issue's slice into a clean, reviewed PR.

**Week 0:** follow [the assignment](weekly/week0/week-00-onboarding.md) for the exact `deliverable0-<handle>` worktree and PR commands. The Issue-specific steps below apply to future tasks.

**1. Pick up an issue.** Read [Use an Issue](#use-an-issue-members), claim your slice and read its acceptance criteria.

**2. Fetch the PM-prepared integration branch.** From your clone:
```sh
git fetch origin
```
The PM/Co-PM creates the integration branch once. If `origin/issue-42/integration` does not exist, ask the PM; members do not create nine separate integration branches.

**3. Create a worktree for your slice:**
```sh
git worktree add -b issue-42/loader ../courtiq-loader origin/issue-42/integration
cd ../courtiq-loader
```
Replace `42` with the actual Issue number and `loader` with your assigned slice. Future slices use their assigned names. Week 0 instead uses the approved flat `deliverable0-<github-handle>` branch and a unique member folder.

**4. Build in small commits.** Each commit should be one coherent step, with a message that says *why*, not just *what*.

**5. Push and open a PR into the integration branch:**
```sh
git push -u origin issue-42/loader
```
Then use the [GitHub PR walkthrough](#open-a-pull-request-members). Write a description explaining what changed and how you verified it. GitHub CLI is an optional alternative, not required.

**6. Respond to review.** Read the whole review before touching anything. Fix what's clearly right yourself; only ask the PM when there's a real judgment call (naming, scope, product behavior). Push follow-up commits and re-request review.

**7. Merge up** once approved (feature → integration), then delete your feature branch and remove the worktree. Move to the next slice.

**You are also a reviewer.** When a teammate requests review, read their PR and leave comments. Reviewing is half the job of being a developer here — it's how we catch bugs before `main` and how everyone learns the codebase.

---

## For Project Managers (managers)

You own the *coordination and the gate to `main`*. You mostly work in GitHub's UI, not the terminal.

### Release Week 0 (PMs)

Week 0 does not require an Issue. Use `deliverable0` as the shared PR destination. Before announcing it:

1. Test/review the prepared assignment and commit the reviewed changes on the existing preparation feature branch, `ali-deliverable0-prep`. Check `git status --short`; preserve/review any listed work before publishing. Never switch dirty preparation onto `main`.
2. Once the preparation is committed and clean, the human PM publishes the target and preparation branches:

```sh
git fetch origin
git branch deliverable0 origin/main
git push -u origin deliverable0
git push -u origin ali-deliverable0-prep
```

If `deliverable0` already exists, reuse it. These are human release commands; agents must not commit/push without explicit instruction.

3. Open a PR with **base** `deliverable0` and **compare** `ali-deliverable0-prep`. Have the Co-PM/teammate review it; address feedback and merge into `deliverable0` with the project's merge-commit workflow. Members start after the target contains the reviewed starter, requirements, database scripts, Compose settings and backup CSV.
4. Confirm members accepted repository invitations and have Write access. On GitHub's **Code** tab, select `deliverable0`, open `weekly/week0/week-00-onboarding.md`, and copy that published file URL. Announce the URL, deadline/time zone and PR base `deliverable0` in Discord.
5. Members use `deliverable0-<github-handle>` and submit only their unique script, with a brief verification summary in the PR description. No screenshots or attachments are required for Week 0. They post their PR links in Discord. Review each against the assignment checklist; approved member PRs merge into `deliverable0`. PMs review `deliverable0` → `main` once all required work is collected.

An Issue can be added later and linked to existing PRs without renaming branches. Future tasks use the standard Issue steps below.

**1. Turn goals into Issues.** Break the project (see [`DELIVERABLES.md`](DELIVERABLES.md)) into issues small enough for one person to finish in a few days. Give each a clear title, acceptance-criteria checklist, and labels. Assign or let members self-assign.

**Prepare the Issue's integration branch once.** Use a clean clone and check `git status --short` first. If it lists existing work, preserve/review that work on its feature branch or ask the Co-PM for help before switching branches. These commands are for a human PM/Co-PM preparing the branch, not an instruction for an agent to publish it:

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c issue-42/integration
git push -u origin issue-42/integration
```

Replace `42` with the newly created Issue number. If the integration branch already exists remotely, reuse it instead of creating another one. Put starter changes on a feature branch/worktree and get its PR into integration reviewed before members begin. For the existing locally prepared onboarding files, coordinate with the Co-PM to preserve and publish that reviewed preparation through this feature → integration process; creating the Issue alone does not make those files available. Share the integration branch name once the starter is present.

**2. Maintain the board.** Keep issues triaged and prioritized so members always know what to pick up next. Link related issues; close duplicates.

**3. Review pull requests.** This is your core review responsibility:
   - Feature → integration PRs can be reviewed by any member or by you.
   - **The integration → `main` PR is yours to review and merge.** Confirm every slice landed, the code-review agent passed, and the acceptance criteria are met.

   Use GitHub's review tools deliberately: **Comment** to ask questions, **Request changes** to block until fixed, **Approve** to sign off. Review the *diff*, not the whole repo.

**4. Gatekeep `main`.** Only you merge to `main`, and only after the integration branch is green and reviewed. Never enable auto-merge on a PR targeting `main`. Prefer **branch protection** on `main` (require a PR + at least one approval) so the rule is enforced, not just trusted.

**5. Keep the team in sync.** After a merge to `main`, remind members to `git pull origin main` before continuing — anyone behind is building on outdated code.

**6. Own the subjective calls.** Members escalate product/UX, naming, dependencies, and architecture decisions to you. Decide, and record the decision in the issue or PR so it's auditable.

---

## Branch naming

For future tasks, namespace every branch by its issue number so the tree is obvious at a glance:

```
issue-<n>/integration        # the root/trunk branch for issue <n>
issue-<n>/<slice-slug>        # a feature/slice branch off the integration branch
```

**Week 0 exception:** shared target `deliverable0`, member features `deliverable0-<github-handle>`. Do not create `deliverable0/<slice>`: a branch named `deliverable0` blocks that ref prefix.

**One hard rule:** inside an `issue-<n>/` namespace, every branch name is a **flat leaf** — no branch name may be a *prefix* of another. Git stores refs as files, so a branch named `issue-1/guide` makes it **impossible** to also create `issue-1/guide/body` (you'll get `cannot lock ref ... 'issue-1/guide' exists`). Use `issue-1/guide` and `issue-1/guide-body` instead.

---

## Worktrees: one issue, one tree

A **worktree** lets you check out multiple branches into **separate folders at the same time**, all backed by the one repository. That's how you build a feature slice without disturbing `main` (or another slice) in your main folder.

```sh
# create a new branch AND a folder for it, based off the integration branch
git worktree add -b issue-42/loader ../PM_REPO_TEMPLATE.worktrees/loader issue-42/integration

# work in that folder like a normal clone
cd ../PM_REPO_TEMPLATE.worktrees/loader
# ...edit, commit, push...

# see all active worktrees
git worktree list

# when the branch is merged and the folder is no longer needed
git worktree remove ../PM_REPO_TEMPLATE.worktrees/loader
```

Why we use them: parallel slices of one issue can each have their own folder, so switching contexts is `cd`, not `git stash` + `git switch`. The whole set of branches under `issue-42/` is that issue's **tree**, and it collapses back into `issue-42/integration` as slices merge up.

---

## Git commands in context

Reach for these at the moments described — not as isolated trivia.

- **`git fetch origin`** — *"What has changed on GitHub?"* Updates your remote-tracking view without changing your files. Safe anytime; do it before deciding whether you're behind.
- **`git pull origin main`** — *"Bring my local `main` up to date."* Fetch + merge in one step. Run before cutting a branch.
- **`git push -u origin <branch>`** — *"Publish my branch."* The `-u` sets upstream so later `git push`/`git pull` need no arguments.
- **`git rebase <base>`** — *"Replay my commits on top of the latest base."* Use it to bring a feature branch forward onto an updated integration branch so your PR is a clean, linear diff. **Only rebase branches that are yours and not yet merged.** Rebasing shared history rewrites commits others may have — don't.
  ```sh
  git switch issue-42/loader
  git fetch origin
  git rebase origin/issue-42/integration
  ```
- **`git merge`** — *"Combine another branch into this one, preserving both histories."* This is how work moves **up the tree** (feature → integration → `main`). We keep merge commits so the small-commit trail stays auditable.
- **`git reset`** — *"Move my branch pointer / unstage things."* Use `git reset --soft HEAD~1` to undo the last *local* commit but keep the changes, or `git restore --staged <file>` to unstage. **Never `git reset --hard` on work you haven't backed up, and never rewrite commits you've already pushed to a shared branch.**
- **`--force` / `--force-with-lease`** — avoid. Only ever force-push a branch that is exclusively yours, and prefer `--force-with-lease` so you don't clobber someone else's push. If you feel you need to force-push a shared branch, stop and ask a PM.

> If a rebase or merge produces conflicts: don't panic. Open the conflicted files, resolve the `<<<<<<<`/`=======`/`>>>>>>>` markers, `git add` them, and continue (`git rebase --continue` or commit the merge). If it's a mess, `git rebase --abort` / `git merge --abort` puts you back where you started.

---

## Code-review agents (strongly recommended)

We **strongly recommend** enabling an automated code-review agent on this repo — **Codex auto-review** (`chatgpt-codex-connector`) or **Claude auto-review**. We do not ship one in this template (you install it on the repo/org), but a project runs much more smoothly with one.

Why it's worth it:
- Every PR gets a fast, consistent first pass **before** a human spends time on it.
- Members get immediate feedback and learn from it; PMs review higher-quality diffs.
- It catches the boring class of bugs (typos, missed edge cases, obvious mistakes) so human review can focus on design and correctness.

How it fits the flow: when a PR opens, the agent reviews it automatically and signals when it's done (Codex reacts on the PR body; a re-review after new commits is requested with a `@codex review` comment). **Wait for that signal, address the findings, then merge up.** The agent is an assistant, not the gate — a human still reviews, and a PM still owns the merge to `main`.

---

## Golden rules

- **Future work starts with an Issue.** Week 0 is the explicit PM-approved exception; its published assignment, Discord deadline and reviewed PRs supply the record.
- **Never push to `main`.** It moves only through a reviewed PR merged by a PM.
- **Sync before you branch.** Cut from an up-to-date `main`; pull often.
- **Small slices, small PRs.** If a PR is sprawling, split it.
- **Merge up the tree** with merge commits — feature → integration → `main`.
- **Review each other's work.** Everyone is a reviewer.
- **Don't rewrite shared history.** No force-push / hard-reset on branches others use.
- **Delete merged branches, keep the commits.** Clean tree, full history.
