# Bulk Branch Management via GitHub API

## Deleting All Branches Except Specific Ones

When you need to clean up a fork/repository and keep only specific branches (e.g., `main` and `beta`):

### Using curl + jq (no gh CLI required)

```bash
# Get all branches, filter out protected ones, delete via API
TOKEN="ghp_xxxxxxxxxxxx"  # PAT with repo scope
OWNER="i-execute"
REPO="hermes-agent"
PROTECTED=("main" "beta")

for page in {1..20}; do
  branches=$(curl -s -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$OWNER/$REPO/branches?per_page=100&page=$page")

  # Exit if no more branches
  [ "$(echo "$branches" | jq 'length')" -eq 0 ] && break

  echo "$branches" | jq -r '.[] | .name' | while read branch; do
    # Skip protected branches
    if [[ " ${PROTECTED[@]} " =~ " ${branch} " ]]; then
      continue
    fi

    # Delete branch ref
    curl -s -X DELETE \
      -H "Authorization: token $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$branch" >/dev/null

    echo "Deleted: $branch"
    sleep 0.1  # Rate limiting
  done
done
```

### One-liner for quick cleanup (100 branches max)

```bash
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/branches?per_page=100" | \
  jq -r '.[] | select(.name != "main" and .name != "beta") | .name' | \
  while read branch; do
    curl -s -X DELETE -H "Authorization: token $TOKEN" \
      "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$branch"
    echo "Deleted: $branch"
  done
```

### Rate limiting notes
- GitHub API: 5000 requests/hour for authenticated requests
- Add `sleep 0.1` between deletions to stay safe
- For 1000+ branches, process in batches with `sleep 60` between pages

## Fork Sync Without gh CLI

```bash
# Add fork remote
git remote add fork https://github.com/YOUR_USER/REPO.git
git fetch fork

# Reset local to match fork
git reset --hard fork/branch-name

# Push local changes to fork
git push fork branch-name

# Delete all other remote branches
git branch -r | grep fork/ | grep -vE "main|beta" | sed 's|fork/||' | \
  xargs -I {} git push fork --delete {}
```

### Keeping Fork in Sync with Upstream
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO.git
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## GitHub PAT Scopes for Repository Management

For full repository management including CI/CD workflows, use a PAT with these scopes:

| Scope | Purpose |
|-------|---------|
| `repo` | Full repo access (read/write code, issues, PRs) |
| `workflow` | Manage GitHub Actions workflows |
| `admin:repo_hook` | Manage repository webhooks |
| `delete_repo` | Delete repositories |
| `admin:org_hook` | Manage organization webhooks |
| `admin:org` | Organization administration |

**Minimal for branch management:** `repo` only
**Full CI/CD + branch cleanup:** `repo`, `workflow`, `admin:repo_hook`, `delete_repo`

## Systemd Service Integration

When running Hermes gateway via systemd:
```bash
# Gateway runs as systemd user service
systemctl --user status hermes-gateway
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway -f

# Must run from OUTSIDE the gateway process
# Gateway cannot restart itself (SIGTERM propagates to children)
```

**Config location:** `~/.hermes/config.yaml`
```yaml
platforms:
  telegram:
    extra:
      rich_messages: true
      rich_drafts: true
```

---

*Added from session: fork cleanup of ~1300 branches on i-execute/hermes-agent (kept only main and beta), Rich Messages deployment, gateway restart workflow.*