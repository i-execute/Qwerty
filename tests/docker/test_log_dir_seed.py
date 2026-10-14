"""Runtime smoke test for Docker $QWERTY_HOME/logs/gateways seeding.

Build the real image and verify logs/ and logs/gateways/ exist and are
owned by the qwerty user after container boot.

Regression guard for #45258: if the first gateway log service runs in
root context, logs/gateways/ is created root-owned; every profile
registered later runs its log service as the dropped qwerty user and
s6-log crash-loops on mkdir: Permission denied.
"""
from __future__ import annotations

from tests.docker.conftest import (
    docker_exec_sh,
    restart_container,
    start_container,
)


def test_logs_gateways_seeded_and_qwerty_owned(
    built_image: str, container_name: str,
) -> None:
    """logs/ and logs/gateways/ must exist and be owned by qwerty after boot."""
    start_container(built_image, container_name)

    # Both directories must exist
    r = docker_exec_sh(
        container_name,
        "test -d /opt/data/logs && "
        "test -d /opt/data/logs/gateways && "
        "echo DIRS_OK || echo DIRS_MISSING",
        timeout=10,
    )
    assert "DIRS_OK" in r.stdout, (
        f"logs/ or logs/gateways/ not seeded: {r.stdout}"
    )

    # Both must be owned by qwerty
    r = docker_exec_sh(
        container_name,
        'logs_owner=$(stat -c "%U" /opt/data/logs); '
        'gateways_owner=$(stat -c "%U" /opt/data/logs/gateways); '
        'echo "logs=$logs_owner gateways=$gateways_owner"',
        timeout=10,
    )
    assert "logs=qwerty" in r.stdout, (
        f"logs/ not owned by qwerty: {r.stdout}"
    )
    assert "gateways=qwerty" in r.stdout, (
        f"logs/gateways/ not owned by qwerty: {r.stdout}"
    )


def test_logs_gateways_healed_when_parent_root_owned(
    built_image: str, container_name: str,
) -> None:
    """Warm-boot stage2 must heal root-owned logs/gateways (#45258).

    Mimics a poisoned volume: QWERTY_HOME already qwerty-owned (so the
    bulk data-volume chown is skipped) while logs/gateways is root-owned.
    Restartable log/run no longer root-chowns that path (symlink TOCTOU),
    so stage2 must repair the parent on every boot.
    """
    start_container(built_image, container_name)

    poison = docker_exec_sh(
        container_name,
        "chown root:root /opt/data/logs/gateways && "
        'home_owner=$(stat -c "%U" /opt/data); '
        'gateways_owner=$(stat -c "%U" /opt/data/logs/gateways); '
        'echo "home=$home_owner gateways=$gateways_owner"',
        user="root",
        timeout=10,
    )
    assert poison.returncode == 0, (poison.stdout, poison.stderr)
    assert "home=qwerty" in poison.stdout, poison.stdout
    assert "gateways=root" in poison.stdout, poison.stdout

    denied = docker_exec_sh(
        container_name,
        "mkdir -p /opt/data/logs/gateways/poison-probe 2>/dev/null "
        "&& echo MKDIR_OK || echo MKDIR_DENIED",
        timeout=10,
    )
    assert "MKDIR_DENIED" in denied.stdout, denied.stdout

    restart_container(container_name)

    healed = docker_exec_sh(
        container_name,
        'gateways_owner=$(stat -c "%U" /opt/data/logs/gateways); '
        "mkdir -p /opt/data/logs/gateways/poison-probe && "
        'echo "gateways=$gateways_owner MKDIR_OK"',
        timeout=10,
    )
    assert healed.returncode == 0, (healed.stdout, healed.stderr)
    assert "gateways=qwerty" in healed.stdout, healed.stdout
    assert "MKDIR_OK" in healed.stdout, healed.stdout
