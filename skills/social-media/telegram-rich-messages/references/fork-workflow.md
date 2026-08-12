# Fork → PR Workflow (no `gh` CLI)
========================================

This reference documents the complete workflow to fork a repo, make changes, and open a PR using only `git` + `curl` (no `gh` CLI needed).

## Prerequisites
- GitHub Personal Access Token (classic) with scopes: `repo`, `workflow`, `read:org`
- Git configured with user.name/user.email

## Step 1: Configure Git Auth
```bash
# One-time setup
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global credential.helper store

# First push will prompt for token (saved in ~/.git-credentials)
# Or pre-configure:
git remote set-url origin https://<USERNAME>:<TOKEN>@github.com/<USERNAME>/<REPO>.git
```

## Step 2: Fork Repo
```bash
# Via GitHub API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ORIGINAL_OWNER/REPO/forks

# Wait ~3 seconds for GitHub to create fork
sleep 3
```

## Step 3: Clone Your Fork
```bash
# Shallow clone for speed
git clone --depth 1 https://github.com/YOUR_USERNAME/REPO.git REPO-fork
cd REPO-fork

# Add upstream for syncing
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO.git
```

## Step 4: Create Feature Branch
```bash
git checkout -b feat/your-feature-name
```

## Step 5: Make Changes
```bash
# Edit files
# ... your changes ...

# Stage & commit
git add -A
git commit -m "feat: descriptive message

- detail 1
- detail 2

Closes #123"
```

## Step 6: Push & Open PR
```bash
git push origin feat/your-feature-name

# Open PR via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ORIGINAL_OWNER/REPO/pulls \
  -d '{
    "title": "feat: your feature title",
    "head": "YOUR_USERNAME:feat/your-feature-name",
    "base": "main",
    "body": "## Summary\n\n## Changes\n- ...\n\n## Testing\n- ..."
  }'
```

## Step 5b (Optional): Sync with Upstream
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## Quick One-Liner PR Creation
```bash
GITHUB_TOKEN=ghp_xxx PR_TITLE="feat: my feature" \
PR_BODY="## Summary\n\n..." \
curl -X POST -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ORIGINAL_OWNER/REPO/pulls \
  -d "$(jq -n --arg title "$PR_TITLE" --arg head "YOUR_USERNAME:feat/your-feature" --arg base "main" --arg body "$PR_BODY" '{title: $title, head: $head, base: $base, body: $body}')"
```

## Security Notes
- Never hardcode tokens in scripts
- Use environment variables: `export GITHUB_TOKEN=ghp_xxx`
- Token in remote URL is visible in `git remote -v` — prefer credential helper
- Rotate tokens periodically