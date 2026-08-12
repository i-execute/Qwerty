# Fork Sync & Branch Cleanup Workflow

This document captures the fork synchronization and branch cleanup patterns used when maintaining a fork of an upstream repository.

## Use Case
- Fork: `i-execute/hermes-agent` from `NousResearch/hermes-agent`
- Working branch: `beta` (all changes)
- Need to sync upstream changes and clean up remote branches

---

## 1. Initial Fork Setup (HTTPS + PAT)

```bash
# Clone the fork
git clone https://github.com/i-execute/hermes-agent.git
cd hermes-agent

# Add upstream remote
git remote add upstream https://github.com/NousResearch/hermes-agent.git
git fetch upstream

# Verify remotes
git remote -v
# origin  -> https://github.com/i-execute/hermes-agent.git (fetch/push)
# upstream -> https://github.com/NousResearch/hermes-agent.git (fetch)
```

---

## 2. Syncing from Upstream

```bash
# Fetch latest upstream changes
git fetch upstream

# Merge upstream/main into local main
git checkout main
git merge upstream/main
git push origin main

# Or rebase local feature branch on upstream/main
git checkout beta
git rebase upstream/main
```

---

## 3. Working on the `beta` Branch

```bash
# Create/switch to beta branch
git checkout -b beta  # or git checkout beta if exists

# Make changes, commit
git add .
git commit -m "feat(telegram): always use Rich Messages for all responses"

# Push to fork
git push origin beta

# Or force push after rebase
git push origin beta --force-with-lease
```

---

## 4. Syncing Fork `beta` with Local

```bash
# If working from another machine, sync local beta with remote
git fetch origin
git checkout beta
git reset --hard origin/beta
```

---

## 5. Bulk Delete All Remote Branches Except `main` and `beta`

**Use case:** Clean up the fork after many feature branches accumulated.

```bash
# List all remote branches on fork
git branch -r | grep "fork/" | grep -vE "main|beta"

# Delete all except main and beta
git branch -r --format='%(refname:short)' | \
  grep -E "^fork/" | \
  grep -vE "main|beta" | \
  sed 's|fork/||' | \
  xargs -I {} git push fork --delete {}
```

**Alternative (more readable):**

```bash
# Get branches to delete
git branch -r | grep -E "^  fork/" | grep -vE "main|beta" | sed 's|  fork/||' > /tmp/branches-to-delete.txt

# Review
cat /tmp/branches-to-delete.txt

# Delete in batches (avoid rate limits)
cat /tmp/branches-to-delete.txt | xargs -I {} git push fork --delete {}
```

**One-liner for automation:**

```bash
git branch -r --format='%(refname:short)' | \
  grep -E "^fork/" | \
  grep -vE "main|beta" | \
  sed 's|fork/||' | \
  xargs -r -n 10 git push fork --delete
```

---

## 6. Local Branch Cleanup

```bash
# Delete local branches that no longer exist on remote
git fetch -p  # prune deleted remotes

# Delete merged local branches
git branch --merged | grep -vE "^\*|main|beta" | xargs -r git branch -d

# Force delete unmerged local branches (careful!)
git branch | grep -vE "^\*|main|beta" | xargs -r git branch -D
```

---

## 7. Complete Sync Workflow (One Command)

```bash
#!/bin/bash
# sync-fork.sh - Run from fork root

set -euo pipefail

echo "🔄 Syncing fork with upstream..."
git fetch upstream
git fetch origin

echo "📦 Updating main..."
git checkout main
git merge upstream/main
git push origin main

echo "🌿 Updating beta (rebase on main)..."
git checkout beta
git rebase main
git push origin beta --force-with-lease

echo "🧹 Deleting all remote branches except main, beta..."
git branch -r --format='%(refname:short)' | \
  grep -E "^fork/" | \
  grep -vE "main|beta" | \
  sed 's|fork/||' | \
  xargs -r -n 10 git push fork --delete

echo "✅ Sync complete!"
```

---

## 8. GitHub PAT for CI/CD

**Token with required scopes:**
- `repo` (full repo access)
- `workflow` (GitHub Actions)
- `admin:repo_hook` (webhooks)
- `admin:org_hook` (org webhooks)

**Add to GitHub Actions secrets:**
```bash
# In GitHub UI: Settings > Secrets and variables > Actions > New repository secret
# Name: GH_TOKEN
# Value: ghp_xxxxxxxxxxxxxxxxxxxx
```

**Use in workflow:**
```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    token: ${{ secrets.GH_TOKEN }}

- name: Push changes
  run: |
    git config user.name "github-actions"
    git config user.email "github-actions@github.com"
    git push origin beta
```

---

## 9. Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `xargs: argument line too long` | Use `xargs -n 10` to batch deletes |
| Rate limit (403) | Add delay: `sleep 1` between deletes or use `xargs -P 1` (serial) |
| "cannot delete branch checked out by other process" | Wait for other CI/CD jobs to finish |
| `git push --delete` fails on protected branch | Remove branch protection first via Settings > Branches |

---

## 10. Related Skills

- `github-auth` — PAT setup and authentication
- `github-pr-workflow` — PR creation and lifecycle
- `github-code-review` — Reviewing changes

---

*Captured from session: Rich Messages implementation for Hermes Agent fork (i-execute/hermes-agent:beta)*