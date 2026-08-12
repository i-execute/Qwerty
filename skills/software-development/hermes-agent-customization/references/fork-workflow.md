# Extended Fork / Sync / PR Workflow for Hermes Agent

Detailed recipes for common fork operations.

## Initial Fork Setup (One-time)

```bash
# Using gh CLI (recommended)
cd ~/.hermes
gh repo fork NousResearch/hermes-agent --clone --remote-name origin
cd hermes-agent
git remote add upstream https://github.com/NousResearch/hermes-agent.git

# Verify
git remote -v
# origin    https://github.com/YOUR-USER/hermes-agent.git (fetch)
# origin    https://github.com/YOUR-USER/hermes-agent.git (push)
# upstream  https://github.com/NousResearch/hermes-agent.git (fetch)
```

## Daily Development: Sync → Branch → Work → PR

```bash
# 1. Sync main with upstream
git fetch upstream
git checkout main
git merge upstream/main --ff-only
git push origin main

# 2. Create feature branch
git checkout -b feat/amazing-new-skill

# 3. Develop... (edit files, write tests)
# ...

# 4. Test locally
make lint          # or: ruff check . && mypy .
pytest -x -q       # or: uv run pytest -x -q

# 5. Commit (conventional commits)
git add -A
git commit -m "feat(skills): add amazing new skill

- Does X, Y, Z
- Includes tests
- Updates docs

Closes #42"

# 6. Push & create PR
git push origin feat/amazing-new-skill
gh pr create --title "feat(skills): add amazing new skill" \
  --body "## Summary
Adds amazing new skill that does X, Y, Z.

## Testing
- [ ] Unit tests pass
- [ ] Manual verification: \`hermes skill load amazing-skill\`

## Checklist
- [ ] Lint passes
- [ ] Tests pass
- [ ] Docs updated
- [ ] No secrets in diff"
```

## Keeping Feature Branch Updated

```bash
# While PR is open, keep it fresh
git fetch upstream
git rebase upstream/main
# Resolve conflicts if any
git push origin feat/amazing-new-skill --force-with-lease
```

## After PR Merged: Cleanup

```bash
# Local
git checkout main
git pull origin main
git branch -d feat/amazing-new-skill

# Remote (gh handles this on merge, but if not)
gh pr view 123 --json headRefName -q .headRefName | xargs git push origin --delete
```

## Working with Multiple PRs (Stacked PRs)

```bash
# Base branch for stack
git checkout -b stack/base upstream/main

# First PR
git checkout -b stack/part1
# ... work ...
git push origin stack/part1
gh pr create --base stack/base --title "feat: part 1"

# Second PR depends on first
git checkout -b stack/part2
# ... work ...
git push origin stack/part2
gh pr create --base stack/part1 --title "feat: part 2"

# Update stack base
git checkout stack/base
git merge upstream/main
git push origin stack/base

# Rebase dependent branches
git checkout stack/part1
git rebase stack/base
git push origin stack/part1 --force-with-lease

git checkout stack/part2
git rebase stack/part1
git push origin stack/part2 --force-with-lease
```

## Handling CI Failures

```bash
# View failed workflow
gh run list --limit 5
gh run view <RUN_ID> --log-failed

# Re-run failed jobs
gh run rerun <RUN_ID> --failed

# Or re-run entire workflow
gh run rerun <RUN_ID>
```

## Managing Secrets for Fork

```bash
# List secrets
gh secret list

# Set secret (for GitHub Actions)
gh secret set DOCKER_TOKEN --body "$DOCKER_TOKEN"
gh secret set NPM_TOKEN --body "$NPM_TOKEN"

# Set repo variable (non-secret)
gh variable set NODE_VERSION --body "20"
```

## Local Development Environment

```bash
# Install in development mode
cd ~/.hermes/hermes-agent
uv pip install -e .[dev]  # or: pip install -e .[dev]

# Run Hermes from source
hermes --help
hermes "test message"

# Run specific test file
pytest tests/test_agent.py -xvs -k "test_memory"

# Watch mode for TDD
ptw tests/ -- -xvs
```

## Common File Patterns

| Change Type | Files to Touch |
|-------------|----------------|
| New skill | `skills/<cat>/<name>/SKILL.md`, `skills/<cat>/<name>/references/`, `skills/<cat>/<name>/templates/` |
| New plugin | `plugins/<name>/plugin.py`, `plugins/<name>/manifest.yaml`, `plugins/<name>/ui/` |
| Core tool | `agent/tools/new_tool.py`, `agent/tools/__init__.py` (register) |
| Config option | `config.yaml` (add), `cli-config.yaml.example` (document) |
| Provider | `providers/<name>/provider.py`, `providers/__init__.py` |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `gh: command not found` | `sudo apt install gh` or `brew install gh` |
| `Permission denied (publickey)` | Add SSH key to GitHub, or use HTTPS with token |
| `push rejected: protected branch` | Push to feature branch, open PR |
| `merge conflict on rebase` | `git status` → edit conflicts → `git add .` → `git rebase --continue` |
| `CI: secret not found` | `gh secret set SECRET_NAME --body "value"` |
| `pytest: import error` | `uv pip install -e .[dev]` or `pip install -e .[dev]` |