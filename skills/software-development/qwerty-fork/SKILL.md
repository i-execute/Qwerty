---
name: qwerty-fork
description: Use when contributing to the Qwerty fork. Keep beta as a shared integration branch, work on personal branches, sync before edits, test first, and merge without force-pushing shared branches.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qwerty, fork, git, beta, collaboration, merge, branches]
    related_skills: [hermes-agent-customization, requesting-code-review]
---

# Qwerty Fork Collaboration Workflow

## Overview

Qwerty uses a protected, cooperative branch workflow. `main` is the stable branch. `beta` is the shared integration branch. Every contributor works on a personal branch, such as `forget`, `kmoella`, or `radiocycle`, and never treats `beta` or `main` as a personal worktree.

This skill is repository policy. Load and follow it before modifying branches, merging work, or pushing Qwerty changes.

## Branch roles

| Branch | Role | Direct work |
|---|---|---|
| `main` | Stable/release line | Only accepted integrations from `beta`; no direct feature work |
| `beta` | Shared integration/testing line | Merge tested contributor branches; never force-push |
| Personal branch | Contributor work | Develop, test, commit, and push here first |

The repository currently has contributor branches including `forget`, `kmoella`, and `radiocycle`. Do not overwrite their history merely to make their tips equal.

## Non-negotiable rules

1. **Never force-push `beta` or `main`.** Use normal merges or pull requests.
2. **Never reset another contributor's branch.** Preserve its commits and inspect its diff before integration.
3. **Sync before editing.** Start from the current `origin/beta`, then update the personal branch.
4. **Test before publishing.** A branch is ready only after focused tests, syntax checks, and a clean diff.
5. **Push personal branches normally.** The branch owner may use `git push --force-with-lease` only on their own branch when explicitly needed; never use plain `--force` on shared branches.
6. **Integrate one contributor at a time.** Fetch, inspect, merge, test, then push `beta`.
7. **Promote beta to main only after beta is verified.** Use a normal fast-forward or an explicit merge commit; never erase main history.
8. **After beta changes, every contributor syncs their own branch before new work.**

## Start work on a personal branch

```bash
cd /home/forget/.hermes/hermes-agent   # or the local Qwerty checkout

git fetch origin --prune
git switch <personal-branch>
git merge --ff-only origin/beta

# Verify the starting point
git status
git log --oneline --decorate -5
```

If `--ff-only` fails, stop and inspect divergence. Do not reset the branch. Use a normal merge or rebase on the personal branch after reviewing the commits:

```bash
git log --oneline --left-right HEAD...origin/beta
git merge origin/beta
```

Completion criterion: the personal branch contains the current beta tip, the working tree is clean, and no unrelated changes are present.

## Develop and verify

Make changes only on the personal branch. Keep commits focused and descriptive.

```bash
git status --short
git diff --check
python -m py_compile <changed-python-files>
pytest -q <focused-tests>
```

For Hermes changes, also inspect the live runtime path when relevant:

```bash
systemctl --user show hermes-gateway.service -p ExecStart -p WorkingDirectory -p MainPID
git branch --show-current
git rev-parse HEAD
```

Never claim tests passed when the test runner or dependency is unavailable. Report the exact blocker.

Completion criterion: focused tests and syntax checks pass, the diff is reviewed, and the commit contains only the intended work.

## Publish a personal branch

```bash
git add <specific-files>
git commit -m "<type>(<scope>): <description>"
git push origin <personal-branch>
```

Use a pull request from `<personal-branch>` into `beta` when review or conflict resolution is useful. Do not push a personal branch's unreviewed work directly into `main`.

## Safely integrate a contributor into beta

Run this from a clean integration checkout. Prefer a pull request; for a local integration use a normal merge:

```bash
cd /home/forget/QwertyWork/Qwerty-sync
git fetch origin --prune
git switch beta
git pull --ff-only origin beta

git diff --stat origin/beta..origin/<personal-branch>
git log --oneline origin/beta..origin/<personal-branch>
git merge --no-ff origin/<personal-branch> -m "merge: integrate <personal-branch> into beta"

# Verify the combined beta before publishing
git diff --check
pytest -q <focused-tests>
git push origin beta
```

If the merge conflicts:

```bash
git status
git diff --name-only --diff-filter=U
# resolve files deliberately, then:
git add <resolved-files>
git commit
pytest -q <focused-tests>
git push origin beta
```

Do not use `git push --force` or `git reset --hard` on `beta`. If verification fails, abort the unpushed merge with `git merge --abort`, fix the contributor branch, and retry.

Completion criterion: `origin/beta` advances through a normal push, the merge commit is present, tests pass, and the remote SHA is verified with `git ls-remote`.

## Promote verified beta to main

Only after beta is tested and accepted:

```bash
git fetch origin --prune
git switch main
git pull --ff-only origin main

git merge --ff-only origin/beta
# If policy requires a merge commit instead, use: git merge --no-ff origin/beta
pytest -q <focused-tests>
git push origin main
```

Completion criterion: `main` contains the verified beta integration and the push is a normal fast-forward or reviewed merge, never a forced update.

## Sync all personal branches after beta changes

Each contributor updates their own branch; an integrator must not rewrite it for them:

```bash
git fetch origin --prune
git switch <personal-branch>
git merge origin/beta
# resolve and test on the personal branch
git push origin <personal-branch>
```

`git pull --rebase origin beta` is also acceptable on a personal branch when the contributor explicitly wants a linear local history. Do not rebase a branch while another contributor is actively building on it without coordination.

## Branch inventory and safety checks

```bash
git branch -a -vv
git ls-remote --heads origin
git status --short
```

Before deleting or changing a branch, confirm its owner and inspect its unique commits:

```bash
git log --oneline origin/beta..origin/<branch>
git diff --stat origin/beta...origin/<branch>
```

Unknown branches are not junk. Preserve them until their work is reviewed or the user explicitly requests deletion.

## Common pitfalls

- **Force-pushing beta:** destroys another contributor's base. Use `git merge --no-ff` and a normal push.
- **Starting from stale beta:** creates avoidable conflicts. Always `fetch` and sync first.
- **Merging directly to main:** bypasses integration testing. Merge into beta first.
- **Using `git pull` with an unspecified strategy:** can create accidental merges. Use explicit `--ff-only`, `merge`, or `rebase`.
- **Assuming equal branch names mean equal content:** inspect SHAs and unique commits.
- **Testing only the personal branch:** test the combined beta after integration too.
- **Switching the live gateway worktree casually:** inspect systemd `ExecStart` first; never replace a running checkout underneath its process.
- **Reporting a push without verification:** compare local SHA with `git ls-remote`.

## Verification checklist

- [ ] Personal work began from current `origin/beta`.
- [ ] No shared branch was force-pushed or reset.
- [ ] Contributor diff and unique commits were inspected.
- [ ] Focused tests, syntax checks, and `git diff --check` passed.
- [ ] Beta integration used a normal merge/PR and was tested after merging.
- [ ] Main promotion happened only after beta verification.
- [ ] Remote SHAs were checked with `git ls-remote`.
- [ ] Other contributor branches were preserved and only synced by their owners.
