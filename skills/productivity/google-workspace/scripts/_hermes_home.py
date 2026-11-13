"""Resolve QWERTY_HOME for standalone skill scripts.

Skill scripts may run outside the Qwerty process (e.g. system Python,
nix env, CI) where ``qwerty_constants`` is not importable.  This module
provides the same ``get_qwerty_home()`` and ``display_qwerty_home()``
contracts as ``qwerty_constants`` without requiring it on ``sys.path``.

When ``qwerty_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``qwerty_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``QWERTY_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from qwerty_constants import display_qwerty_home as display_qwerty_home
    from qwerty_constants import get_qwerty_home as get_qwerty_home
except (ModuleNotFoundError, ImportError):

    def get_qwerty_home() -> Path:
        """Return the Qwerty home directory (default: ~/.qwerty).

        Mirrors ``qwerty_constants.get_qwerty_home()``."""
        val = os.environ.get("QWERTY_HOME", "").strip()
        return Path(val) if val else Path.home() / ".qwerty"

    def display_qwerty_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``qwerty_constants.display_qwerty_home()``."""
        home = get_qwerty_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
