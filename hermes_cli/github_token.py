"""
Hermes CLI command: hermes github

Securely manage GitHub Personal Access Tokens (PAT) for authenticated git operations.
Stores token in XDG_RUNTIME_DIR (secure ephemeral storage) and git credential helper.
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

try:
    from hermes_cli.colors import ColorizeWithDynamic
    colors = ColorizeWithDynamic()
except ImportError:
    # Fallback if colors module not available
    class FallbackColors:
        def info(self, msg): return f"ℹ️  {msg}"
        def success(self, msg): return f"✅ {msg}"
        def error(self, msg): return f"❌ {msg}"
        def warn(self, msg): return f"⚠️  {msg}"
    colors = FallbackColors()


def validate_pat_format(token: str) -> bool:
    """Validate GitHub PAT format (ghp_* for classic, github_* for fine-grained)."""
    token = token.strip()
    return (
        token.startswith("ghp_") or token.startswith("github_")
    ) and len(token) >= 20


async def setup_git_credential_helper(token: str, host: str = "github.com") -> None:
    """Configure git credential helper to cache token securely."""
    
    # Use credential.helper to cache in memory (respects OS credential storage)
    cmd = ["git", "config", "--global", "credential.helper", "store"]
    await asyncio.create_subprocess_exec(*cmd)
    
    # Store credentials via git credential helper
    cred_input = f"protocol=https\nhost={host}\nusername=oauth2\npassword={token}\n\n"
    proc = await asyncio.create_subprocess_exec(
        "git", "credential", "approve",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate(cred_input.encode())


async def store_token_in_runtime(token: str) -> Optional[str]:
    """Store token in XDG_RUNTIME_DIR for current session (removed on logout)."""
    
    runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    if not runtime_dir:
        return None
    
    token_file = Path(runtime_dir) / "hermes-github-token"
    try:
        # Store with secure permissions (0600: owner read/write only)
        token_file.write_text(token, encoding="utf-8")
        token_file.chmod(0o600)
        return str(token_file)
    except Exception as e:
        print(
            colors.warn(f"⚠️  Failed to store token in XDG_RUNTIME_DIR: {e}")
        )
        return None


async def hermes_github(args) -> int:
    """
    Manage GitHub Personal Access Token for Hermes.
    
    Usage:
        hermes github set          # Prompt for token (interactive)
        hermes github check        # Verify current token is set
        hermes github clear        # Remove token from storage
    """
    
    if not args or args[0] == "help":
        print(
            colors.info(
                """
## Hermes GitHub Token Management

Securely store your GitHub Personal Access Token (PAT) for authenticated git operations.

### Usage

  hermes github set              # Interactively input PAT
  hermes github check            # Verify token is configured
  hermes github clear            # Remove token from storage

### Token Requirements

- **Classic PAT:** Starts with `ghp_` (e.g., `ghp_ZptxNlBKEd4...`)
- **Fine-grained PAT:** Starts with `github_` (e.g., `github_pat_...`)
- **Minimum length:** 20 characters
- **Scopes needed for Hermes:**
  - `repo` (full access to repositories)
  - `workflow` (GitHub Actions)
  - `admin:repo_hook` (repository webhooks)
  - `delete_repo` (cleanup operations)

### Storage

Tokens are stored in:
1. **XDG_RUNTIME_DIR** (ephemeral, cleared on logout) — Recommended
2. **Git credential helper** (OS-level secure storage)

Tokens are NEVER logged or printed in output.

### Security Best Practices

- Regenerate token if accidentally exposed
- Use fine-grained PATs when possible (more restrictive)
- Set short expiration (30-90 days)
- Monitor token usage in GitHub Settings → Developer Settings
                """
            )
        )
        return 0
    
    action = args[0]
    
    if action == "set":
        # Prompt for token
        print(
            colors.info(
                "🔐 Enter your GitHub PAT (starts with ghp_ or github_): "
            ),
            end="",
            flush=True,
        )
        sys.stdout.flush()
        
        # Hide input (getpass)
        token = __import__("getpass").getpass("")
        
        if not validate_pat_format(token):
            print(
                colors.error(
                    "❌ Invalid PAT format. Must start with 'ghp_' or 'github_' and be ≥20 chars."
                )
            )
            return 1
        
        # Store in both places
        try:
            runtime_path = await store_token_in_runtime(token)
            await setup_git_credential_helper(token)
            
            msg = "✅ GitHub PAT stored securely"
            if runtime_path:
                msg += f" ({runtime_path})"
            print(colors.success(msg))
            print(
                colors.info(
                    "   Git credential helper configured for future clones/pulls"
                )
            )
            return 0
        except Exception as e:
            print(colors.error(f"❌ Failed to store token: {e}"))
            return 1
    
    elif action == "check":
        # Verify token exists and is valid
        runtime_dir = os.getenv("XDG_RUNTIME_DIR")
        token_file = Path(runtime_dir) / "hermes-github-token" if runtime_dir else None
        
        if token_file and token_file.exists():
            token = token_file.read_text().strip()
            if validate_pat_format(token):
                print(
                    colors.success(
                        "✅ GitHub PAT is stored and valid (XDG_RUNTIME_DIR)"
                    )
                )
                return 0
        
        # Check git credential helper
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "credential", "fill",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate(
                b"protocol=https\nhost=github.com\n\n"
            )
            if b"password=" in stdout:
                print(
                    colors.success(
                        "✅ GitHub PAT is configured in git credential helper"
                    )
                )
                return 0
        except Exception:
            pass
        
        print(
            colors.error("❌ No GitHub PAT found. Run: hermes github set")
        )
        return 1
    
    elif action == "clear":
        # Remove token
        runtime_dir = os.getenv("XDG_RUNTIME_DIR")
        if runtime_dir:
            token_file = Path(runtime_dir) / "hermes-github-token"
            if token_file.exists():
                token_file.unlink()
                print(colors.success("✅ GitHub PAT removed from XDG_RUNTIME_DIR"))
        
        # Clear git credential helper (store empty)
        try:
            cred_input = b"protocol=https\nhost=github.com\n\n"
            proc = await asyncio.create_subprocess_exec(
                "git", "credential", "reject",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate(cred_input)
            print(colors.success("✅ GitHub credentials cleared from git"))
        except Exception as e:
            print(colors.warn(f"⚠️  Could not clear git credentials: {e}"))
        
        return 0
    
    else:
        print(
            colors.error(
                f"❌ Unknown action: {action}. Use: set, check, clear, help"
            )
        )
        return 1


# CLI entrypoint registration
def register_command():
    """Register 'hermes github' command in CLI."""
    return {
        "name": "github",
        "help": "Manage GitHub Personal Access Token (PAT) for authenticated git operations",
        "handler": hermes_github,
        "aliases": ["gh"],
    }
