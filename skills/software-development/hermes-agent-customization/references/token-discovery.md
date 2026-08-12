# GitHub Token Discovery in Userbot Configurations

Reference for locating existing GitHub tokens in userbot (Heroku/Hikka) configuration files.

## Primary Locations

### 1. Main Config JSON (`config-<user_id>.json`)
```json
{
  "AetherAI": {
    "__config__": {
      "github_token": "ghp_xxxxxxxxxxxx"
    }
  }
}
```
**Path:** `/home/forget/Heroku/config-7610246474.json` (example)
**Key:** `AetherAI.__config__.github_token`

### 2. Loaded Module Python Files (`loaded_modules/<Module>_<user_id>.py`)
```python
loader.ConfigValue(
    "github_token",
    "",
    "GitHub токен для git-операций (gh CLI должен быть установлен).",
    validator=loader.validators.Hidden()
)
```
**Pattern:** `loader.ConfigValue("github_token", ...)`
**Note:** Default value is often empty string `""`

### 3. Environment Files
```bash
# ~/.hermes/.env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Project .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## Search Commands

```bash
# Search all JSON configs
grep -r "github_token" /home/forget/Heroku/ --include="*.json"

# Search loaded modules
grep -r "ConfigValue.*github_token" /home/forget/Heroku/loaded_modules/

# Search .env files
grep -r "GITHUB_TOKEN" /home/forget/ --include="*.env" 2>/dev/null
```

## Scopes Required for Hermes Agent Development

| Scope | Purpose |
|-------|---------|
| `repo` | Full repo access: push, PR, issues, releases |
| `workflow` | GitHub Actions: trigger, manage, secrets |
| `read:org` | Organization repos (if working in org) |

## Creating a New PAT (Personal Access Token)

1. Go to: https://github.com/settings/tokens/new
2. **Name:** `hermes-agent-fork-<date>`
3. **Expiration:** 90 days (recommended) or No expiration
4. **Scopes:** ✅ `repo` ✅ `workflow` ✅ `read:org`
5. **Generate** → Copy immediately (shown once)

## Token Format

- **Classic PAT:** `ghp_` + 36 chars (40 total)
- **Fine-grained:** `github_pat_` + 82 chars

Both work with `gh` CLI and git credential helper.

## Verification

```bash
# Test token works
gh auth status
# or
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```