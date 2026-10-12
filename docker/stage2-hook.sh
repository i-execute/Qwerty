#!/bin/sh
# s6-overlay stage2 hook — runs as root after the supervision tree is
# up but before user services start. Handles UID/GID remap, volume
# chown, config seeding, and skills sync.
#
# Per-service privilege drop happens inside each service's `run` script
# (and in main-wrapper.sh) via s6-setuidgid, not here.
#
# Wired into the image as /etc/cont-init.d/01-qwerty-setup by the
# Dockerfile. The shim at docker/entrypoint.sh forwards to this script
# so external references to docker/entrypoint.sh still work.
#
# NB: cont-init.d scripts run with no arguments — the user's CMD args
# are NOT visible here. That's fine: we use Architecture B (s6-overlay
# main-program model), so main-wrapper.sh runs the CMD with full
# stdin/stdout/stderr access and handles arg parsing there.

set -eu

QWERTY_HOME="${QWERTY_HOME:-/opt/data}"
INSTALL_DIR="/opt/qwerty"

# Drop to qwerty via s6-setuidgid, but skip it when already non-root.
as_qwerty() { [ "$(id -u)" = 0 ] || { "$@"; return; }; s6-setuidgid qwerty "$@"; }

# --- Reject the unsupported `docker run --user <uid>:<gid>` start ---
# Detect the case where the container was launched with `--user` pinned to an
# arbitrary host UID (the classic `--user $(id -u):$(id -g)` invocation people
# used in the tini era to make container-written files match their host user).
#
# Under s6-overlay this no longer works: the bootstrap (UID remap, data-volume
# ownership, config seeding) requires root, and it is skipped when the container
# starts non-root. The baked install tree under /opt/qwerty is intentionally
# root-owned and non-writable; mutable runtime state must live under
# $QWERTY_HOME. An arbitrary `--user` UID therefore cannot repair or populate
# the data volume, and startup fails with EACCES. See #34837 for the
# supervision-tree side of this.
#
# The supported way to match host-side ownership is to start as root (the image
# default) and pass QWERTY_UID/QWERTY_GID — or the PUID/PGID aliases — which the
# remap block below consumes via usermod/groupmod + targeted chown. That gives
# the exact same outcome (files owned by your host UID) without breaking s6.
#
# preinit runs setuid-root (euid=0) but cont-init.d hooks run with the real UID
# the container was started as, so `id -u` here is the host UID (e.g. 1000), and
# `id -u qwerty` is the unremapped build UID (10000) because no root-only remap
# could run. root starts (id -u = 0) and the normal supervised drop to the
# qwerty UID are both unaffected.
cur_uid="$(id -u)"
if [ "$cur_uid" != 0 ] && [ "$cur_uid" != "$(id -u qwerty)" ]; then
    cat >&2 <<EOF
[stage2] ERROR: container started with --user $cur_uid (an arbitrary, non-qwerty UID).

This is not supported under the s6-overlay image. The container bootstrap
(UID remap, data-volume ownership, config seeding) needs to start as root,
and the baked /opt/qwerty install tree is intentionally root-owned and
non-writable, so a pinned --user UID cannot repair startup state — startup
will fail.

To make container-written files match your HOST user, DON'T use --user.
Start the container as root (the default) and pass your host UID/GID instead:

    docker run -e QWERTY_UID=\$(id -u) -e QWERTY_GID=\$(id -g) ...

NAS users (Synology / unRAID / UGOS) can use the PUID/PGID aliases:

    docker run -e PUID=\$(id -u) -e PGID=\$(id -g) ...

The image remaps the qwerty user to that UID/GID at boot and chowns the data
volume accordingly, so files land owned by your host user — the same outcome
--user was being used for, without breaking the supervision tree.
EOF
    exit 1
fi

# --- Bootstrap QWERTY_HOME as root ---
# Create the directory (and any missing parents) while we still have root
# privileges so the chown checks below see real metadata and the later
# `s6-setuidgid qwerty mkdir -p` block doesn't EACCES on root-owned
# ancestors. Without this, custom QWERTY_HOME paths whose parents only
# root can create (e.g. `QWERTY_HOME=/home/qwerty/.qwerty` in a Compose
# file, or any path under a fresh / not pre-populated by the image)
# fail on first boot with `mkdir: cannot create directory '/...': Permission
# denied` and the cont-init hook exits non-zero. Idempotent — `mkdir -p`
# is a no-op if the dir already exists. (#18482, salvages #18488)
mkdir -p "$QWERTY_HOME"

# Numeric UID/GID validation: must be digits only, non-root, 1-65534.
# NAS hosts such as Unraid commonly use low non-root IDs (99:100).
validate_uid_gid() {
    case "$1" in
        ''|*[!0-9]*) return 1 ;;
        *) [ "$1" -ge 1 ] && [ "$1" -le 65534 ] ;;
    esac
}

# --- UID/GID remap ---
# Accept PUID/PGID as aliases for QWERTY_UID/QWERTY_GID.  NAS users (UGOS,
# Synology, unRAID) expect the LinuxServer.io PUID/PGID convention and
# bind-mount /opt/data from a host directory owned by their own UID; without
# this alias those vars are silently ignored and the s6-setuidgid drop to
# UID 10000 leaves the runtime unable to read the volume.  QWERTY_UID/
# QWERTY_GID still win when both are set.  See #15290, salvages #25872.
QWERTY_UID="${QWERTY_UID:-${PUID:-}}"
QWERTY_GID="${QWERTY_GID:-${PGID:-}}"

if [ -n "${QWERTY_UID:-}" ] && validate_uid_gid "$QWERTY_UID" && [ "$QWERTY_UID" != "$(id -u qwerty)" ]; then
    echo "[stage2] Changing qwerty UID to $QWERTY_UID"
    usermod -u "$QWERTY_UID" qwerty
fi
if [ -n "${QWERTY_GID:-}" ] && validate_uid_gid "$QWERTY_GID" && [ "$QWERTY_GID" != "$(id -g qwerty)" ]; then
    echo "[stage2] Changing qwerty GID to $QWERTY_GID"
    # -o allows non-unique GID (e.g. macOS GID 20 "staff" may already
    # exist as "dialout" in the Debian-based container image).
    groupmod -o -g "$QWERTY_GID" qwerty 2>/dev/null || true
fi

# --- Docker socket group membership (docker-in-docker / DooD) ---
# When the user bind-mounts the host Docker daemon socket
# (`-v /var/run/docker.sock:/var/run/docker.sock`) to use the `docker`
# terminal backend from inside the container, the socket is owned by the
# host's `docker` group (or root). The supervised qwerty user (UID 10000)
# is not a member of any group that matches the socket's GID, so every
# `docker` invocation EACCES'es and `check_terminal_requirements()` fails.
# See #16703.
#
# Granting the supp group via `docker run --group-add <gid>` alone is
# NOT sufficient with our s6-setuidgid privilege drop: s6-setuidgid (and
# gosu, the older shim) calls initgroups() for the target user, which
# rebuilds the supplementary group list from /etc/group. Without an
# /etc/group entry whose GID matches the socket, the kernel-granted
# supp group is silently wiped between PID 1 and the dropped process.
# Confirmed empirically: `--group-add 998` alone leaves the dropped
# qwerty process with `Groups: 10000` (998 gone); after this hook adds
# the entry, the dropped process has `Groups: 998 10000` as expected.
#
# Fix: detect the socket's GID at boot and ensure /etc/group has a
# matching entry that includes qwerty. Idempotent across container
# restarts. Skipped silently when no socket is bind-mounted.
#
# Handles the awkward corner cases:
#   - socket owned by GID 0 (root) — some Podman setups; usermod -aG root
#   - socket GID already used by a known container group (e.g. tty=5):
#     reuse that group's name rather than creating a duplicate
#   - qwerty is already a member of the right group (idempotent restart)
#   - chown/groupadd failures under rootless containers — non-fatal
for sock in /var/run/docker.sock /run/docker.sock; do
    [ -S "$sock" ] || continue
    sock_gid=$(stat -c '%g' "$sock" 2>/dev/null) || continue
    [ -n "$sock_gid" ] || continue
    # Already a member? Nothing to do.
    if id -G qwerty 2>/dev/null | tr ' ' '\n' | grep -qx "$sock_gid"; then
        echo "[stage2] qwerty already in group $sock_gid for $sock"
        break
    fi
    # Resolve or create a group name for this GID.
    sock_group=$(getent group "$sock_gid" 2>/dev/null | cut -d: -f1)
    if [ -z "$sock_group" ]; then
        sock_group="hostdocker"
        if ! groupadd -g "$sock_gid" "$sock_group" 2>/dev/null; then
            echo "[stage2] Warning: groupadd -g $sock_gid $sock_group failed; skipping docker socket group setup"
            break
        fi
        echo "[stage2] Created group $sock_group (GID $sock_gid) for Docker socket"
    fi
    if usermod -aG "$sock_group" qwerty 2>/dev/null; then
        echo "[stage2] Added qwerty to group $sock_group (GID $sock_gid) for $sock"
    else
        echo "[stage2] Warning: usermod -aG $sock_group qwerty failed; docker backend may fail with EACCES"
    fi
    break
done

# --- Fix ownership of data volume ---
# When QWERTY_UID is remapped or the top-level $QWERTY_HOME isn't owned by
# the runtime qwerty UID, restore ownership to qwerty — but ONLY for the
# directories qwerty actually writes to. The full $QWERTY_HOME may be a
# host-mounted bind containing unrelated user files; `chown -R` would
# silently destroy host ownership of those (see issue #19788).
#
# The canonical list of qwerty-owned subdirs is the same one the s6-setuidgid
# mkdir -p block below seeds. Keep them in sync if the seed list changes.
actual_qwerty_uid=$(id -u qwerty)

path_has_symlink_component() {
    path="$1"
    root="${2:-$QWERTY_HOME}"
    while [ -n "$path" ] && [ "$path" != "/" ]; do
        if [ -L "$path" ]; then
            return 0
        fi
        if [ "$path" = "$root" ]; then
            break
        fi
        parent="$(dirname "$path")"
        if [ "$parent" = "$path" ]; then
            break
        fi
        path="$parent"
    done
    return 1
}

refuse_symlinked_path() {
    action="$1"
    target="$2"
    if path_has_symlink_component "$target"; then
        echo "[stage2] Warning: refusing $action through symlinked path $target — continuing"
        return 0
    fi
    return 1
}

chown_qwerty_tree() {
    target="$1"
    if refuse_symlinked_path "recursive chown" "$target"; then
        return 0
    fi
    chown -R qwerty:qwerty "$target" 2>/dev/null || \
        echo "[stage2] Warning: chown $target failed (rootless container?) — continuing"
}

needs_chown=false
if [ "$(stat -c %u "$QWERTY_HOME" 2>/dev/null)" != "$actual_qwerty_uid" ]; then
    needs_chown=true
fi
if [ "$needs_chown" = true ]; then
    echo "[stage2] Fixing ownership of $QWERTY_HOME (targeted) to qwerty ($actual_qwerty_uid)"
    # In rootless Podman the container's "root" is mapped to an
    # unprivileged host UID — chown will fail. That's fine: the volume
    # is already owned by the mapped user on the host side.
    #
    # Top-level $QWERTY_HOME: chown the directory itself (not its contents)
    # so qwerty can mkdir new subdirs but bind-mounted host files keep
    # their existing ownership.
    if refuse_symlinked_path "chown" "$QWERTY_HOME"; then
        :
    else
        chown qwerty:qwerty "$QWERTY_HOME" 2>/dev/null || \
            echo "[stage2] Warning: chown $QWERTY_HOME failed (rootless container?) — continuing"
    fi
    # Qwerty-owned subdirs: recursive chown is safe here because these are
    # created and managed exclusively by qwerty (see the s6-setuidgid mkdir
    # -p block below for the canonical list).
    for sub in cron sessions logs hooks memories skills skins plans workspace home profiles pairing platforms/pairing lazy-packages; do
        if [ -e "$QWERTY_HOME/$sub" ]; then
            chown_qwerty_tree "$QWERTY_HOME/$sub"
        fi
    done
fi

# --- Immutable install tree ---
# Do not chown runtime code or dependency trees under $INSTALL_DIR back to the
# qwerty user. Hosted/container instances keep mutable state under
# $QWERTY_HOME (/opt/data) and run with PYTHONDONTWRITEBYTECODE plus
# QWERTY_DISABLE_LAZY_INSTALLS=1. Keeping /opt/qwerty root-owned and
# non-writable prevents an agent session from self-modifying the installed
# source, venv, TUI bundle, or node_modules and bricking the gateway.
#
# Lazy-installable optional backends (Firecrawl, Exa, Feishu, etc.) cannot
# install into the sealed venv, so they are redirected to the writable
# $QWERTY_HOME/lazy-packages dir on the data volume (Dockerfile sets
# QWERTY_LAZY_INSTALL_TARGET). That dir is appended to the END of sys.path,
# so a package installed there can only ADD modules — it can never shadow or
# break a core module, which is what keeps the sealed-venv guarantee intact
# even though installs are re-enabled. The dir is seeded + chowned to qwerty
# in the mkdir/chown blocks above so first-use installs succeed as the
# unprivileged runtime user, and it persists across container recreates /
# image updates (an ABI stamp wipes it if a rebuild bumps the interpreter).

# Always reset ownership of $QWERTY_HOME/profiles to qwerty on every
# boot. Profile dirs and files can land owned by root when commands
# are invoked via `docker exec <container> qwerty …` (which defaults
# to root unless `-u` is passed), and that breaks the cont-init
# reconciler (02-reconcile-profiles) which runs as qwerty and walks
# the profiles dir. Idempotent; skipped on rootless containers where
# chown would fail.
if [ -d "$QWERTY_HOME/profiles" ]; then
    chown_qwerty_tree "$QWERTY_HOME/profiles"
fi

# Always reset ownership of $QWERTY_HOME/cron on every boot for the same
# docker-exec/root-write reason as profiles/. The cron scheduler state
# (jobs.json) must stay readable by the unprivileged qwerty runtime even
# after root-context maintenance commands or scheduler writes.
if [ -d "$QWERTY_HOME/cron" ]; then
    chown_qwerty_tree "$QWERTY_HOME/cron"
fi

# Always ensure logs/gateways is qwerty-owned (#45258). Formerly healed by
# restartable gateway log/run chown — removed due to symlink TOCTOU
# (CWE-59/367). The targeted data-volume chown above only runs when the
# top-level $QWERTY_HOME is mis-owned, so a warm volume with qwerty-owned
# QWERTY_HOME but root-owned logs/gateways would otherwise leave
# s6-setuidgid qwerty mkdir failing with Permission denied. Non-recursive:
# profile leaf dirs are each created/owned by their own log/run as qwerty.
if [ -d "$QWERTY_HOME/logs/gateways" ]; then
    if refuse_symlinked_path "chown" "$QWERTY_HOME/logs/gateways"; then
        :
    else
        chown qwerty:qwerty "$QWERTY_HOME/logs/gateways" 2>/dev/null || true
    fi
fi

# Always reset ownership of pairing data on every boot, same docker-exec/
# root-write reason as profiles/ and cron/. `docker exec <container>
# qwerty pairing approve …` defaults to uid=0 and writes 0600 root-owned
# approval files that the unprivileged qwerty gateway cannot read,
# silently leaving the approved user unauthorized (#10270). The targeted
# data-volume chown above only runs when the top-level $QWERTY_HOME is
# mis-owned, so warm boots skip it — this block makes a container restart
# self-heal. Tiny directory (a handful of small JSON files), so the cost
# is negligible.
if [ -d "$QWERTY_HOME/platforms/pairing" ]; then
    chown_qwerty_tree "$QWERTY_HOME/platforms/pairing"
fi
# Legacy location (pre-consolidated layout).
if [ -d "$QWERTY_HOME/pairing" ]; then
    chown_qwerty_tree "$QWERTY_HOME/pairing"
fi

# Reset ownership of qwerty-owned top-level state files on every boot.
# The targeted data-volume chown above only covers qwerty-owned
# *subdirectories*; loose state files living directly under $QWERTY_HOME
# are missed. When those files are created or rewritten by
# `docker exec <container> qwerty …` (root unless `-u` is passed) they
# land root-owned, and the unprivileged qwerty runtime then hits
# PermissionError on next startup (e.g. gateway.lock / state.db /
# auth.json), producing a gateway restart loop.
#
# We use an explicit allowlist rather than a blanket `find -user root`
# sweep so host-owned files in a bind-mounted $QWERTY_HOME are never
# touched — same targeted-ownership contract as the subdir chown above
# (issue #19788, PR #19795). The list mirrors the top-level *file*
# entries of qwerty_cli.profile_distribution.USER_OWNED_EXCLUDE plus the
# runtime lock files; keep them in sync if that set changes.
for f in \
    auth.json auth.lock .env \
    state.db state.db-shm state.db-wal \
    qwerty_state.db \
    response_store.db response_store.db-shm response_store.db-wal \
    gateway.pid gateway.lock gateway_state.json processes.json \
    active_profile; do
    if [ -e "$QWERTY_HOME/$f" ]; then
        if refuse_symlinked_path "chown" "$QWERTY_HOME/$f"; then
            :
        else
            chown qwerty:qwerty "$QWERTY_HOME/$f" 2>/dev/null || true
        fi
    fi
done

# --- config.yaml permissions ---
# Ensure config.yaml is readable by the qwerty runtime user even if it
# was edited on the host after initial ownership setup.
if [ -f "$QWERTY_HOME/config.yaml" ]; then
    if refuse_symlinked_path "chown/chmod" "$QWERTY_HOME/config.yaml"; then
        :
    else
        chown qwerty:qwerty "$QWERTY_HOME/config.yaml" 2>/dev/null || true
        chmod 640 "$QWERTY_HOME/config.yaml" 2>/dev/null || true
    fi
fi

# --- Seed directory structure as qwerty user ---
# Run as qwerty via s6-setuidgid so dirs end up owned correctly (matters
# under rootless Podman where chown back to root would fail).
#
# Use direct `mkdir -p` invocation (no `sh -c "..."` wrapper) so the
# shell isn't a second interpreter — defends against $QWERTY_HOME values
# containing shell metacharacters. PR #30136 review item O2.
as_qwerty mkdir -p \
    "$QWERTY_HOME/backups" \
    "$QWERTY_HOME/cron" \
    "$QWERTY_HOME/sessions" \
    "$QWERTY_HOME/logs" \
    "$QWERTY_HOME/logs/gateways" \
    "$QWERTY_HOME/hooks" \
    "$QWERTY_HOME/memories" \
    "$QWERTY_HOME/skills" \
    "$QWERTY_HOME/skins" \
    "$QWERTY_HOME/plans" \
    "$QWERTY_HOME/workspace" \
    "$QWERTY_HOME/home" \
    "$QWERTY_HOME/pairing" \
    "$QWERTY_HOME/platforms/pairing" \
    "$QWERTY_HOME/lazy-packages"

# --- Install-method stamp ---
# The 'docker' stamp is baked into the immutable install tree at
# /opt/qwerty/.install_method (see Dockerfile), NOT written here into
# $QWERTY_HOME. detect_install_method() reads the code-scoped stamp first.
#
# Why we no longer stamp $QWERTY_HOME: it is a shared DATA volume, commonly
# bind-mounted from the host (~/.qwerty:/opt/data) and sometimes shared with a
# host-side Desktop/CLI install. Stamping 'docker' here clobbered that host
# install's marker, so its in-app updater read 'docker' and refused to run
# 'qwerty update'. To heal homes already poisoned by older images, remove a
# stale 'docker' stamp from $QWERTY_HOME if one is present (the host install's
# own installer re-creates its code-scoped stamp; a genuine container relies on
# the baked /opt/qwerty stamp, so deleting the data-dir copy is safe).
if [ -f "$QWERTY_HOME/.install_method" ]; then
    stamped="$(tr -d '[:space:]' < "$QWERTY_HOME/.install_method" 2>/dev/null || true)"
    if [ "$stamped" = "docker" ]; then
        rm -f "$QWERTY_HOME/.install_method" 2>/dev/null || true
    fi
fi

# --- Seed config files (only on first boot) ---
seed_one() {
    dest=$1
    src=$2
    if [ ! -f "$QWERTY_HOME/$dest" ] && [ -f "$INSTALL_DIR/$src" ]; then
        if refuse_symlinked_path "seed" "$QWERTY_HOME/$dest"; then
            :
        else
            as_qwerty cp "$INSTALL_DIR/$src" "$QWERTY_HOME/$dest"
        fi
    fi
}
seed_one ".env" ".env.example"
seed_one "config.yaml" "cli-config.yaml.example"
seed_one "SOUL.md" "docker/SOUL.md"

# .env holds API keys and secrets — restrict to owner-only access. Applied
# unconditionally (not only on first-seed) so a host-mounted .env that was
# created with a permissive umask gets tightened on every container start.
if [ -f "$QWERTY_HOME/.env" ]; then
    if refuse_symlinked_path "chown/chmod" "$QWERTY_HOME/.env"; then
        :
    else
        chown qwerty:qwerty "$QWERTY_HOME/.env" 2>/dev/null || true
        chmod 600 "$QWERTY_HOME/.env" 2>/dev/null || true
    fi
fi

# --- Migrate persisted config schema ---
# Docker image upgrades replace the code under $INSTALL_DIR but preserve
# $QWERTY_HOME on the mounted volume. Run the same safe, non-interactive
# config-schema migrations that `qwerty update` runs for non-Docker installs,
# after first-boot seeding and before supervised gateway services start.
# Set QWERTY_SKIP_CONFIG_MIGRATION=1 for controlled/manual migrations.
if [ -f "$QWERTY_HOME/config.yaml" ]; then
    s6-setuidgid qwerty "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/scripts/docker_config_migrate.py" \
        || echo "[stage2] Warning: docker_config_migrate.py failed; continuing"
fi

# auth.json: bootstrap from env on first boot only. Same semantics as the
# pre-s6 entrypoint — the [ ! -f ] guard is critical to avoid clobbering
# rotated refresh tokens on container restart.
if [ ! -f "$QWERTY_HOME/auth.json" ] && [ -n "${QWERTY_AUTH_JSON_BOOTSTRAP:-}" ]; then
    if refuse_symlinked_path "seed" "$QWERTY_HOME/auth.json"; then
        :
    else
        printf '%s' "$QWERTY_AUTH_JSON_BOOTSTRAP" > "$QWERTY_HOME/auth.json"
        chown qwerty:qwerty "$QWERTY_HOME/auth.json" 2>/dev/null || true
        chmod 600 "$QWERTY_HOME/auth.json"
    fi
fi

# auth.json: re-seed a TERMINALLY-DEAD Nous bootstrap session (self-heal).
#
# The [ ! -f ] guard above deliberately refuses to clobber an existing
# auth.json, so a container whose Nous bootstrap session took a terminal
# invalid_grant (tokens cleared, providers.nous.last_auth_error.relogin_required
# stamped) can NOT recover from a plain restart — it stays unauthenticated until
# the credential is replaced. An orchestrator that manages the container can
# supply a freshly-issued session via QWERTY_AUTH_JSON_REBOOTSTRAP (distinct
# from the create-only *_BOOTSTRAP var); this helper swaps ONLY the
# providers.nous entry when the on-disk entry is provably terminal OR the
# orchestrator seed has a later obtained_at timestamp. The latter covers the
# stop/update/start sequence where NAS already revoked the still-healthy-looking
# local session. Older/incomparable seeds remain no-ops, so leaving the env set
# cannot roll a healthy rotated token backward. Runs as its own stdlib-only
# subprocess (no app imports) and always exits 0.
if [ -f "$QWERTY_HOME/auth.json" ] && [ -n "${QWERTY_AUTH_JSON_REBOOTSTRAP:-}" ]; then
    if refuse_symlinked_path "reseed" "$QWERTY_HOME/auth.json"; then
        :
    else
        s6-setuidgid qwerty "$INSTALL_DIR/.venv/bin/python" \
            "$INSTALL_DIR/scripts/docker_rebootstrap_nous_session.py" \
            "$QWERTY_HOME/auth.json" \
            || echo "[stage2] Warning: docker_rebootstrap_nous_session.py failed; continuing"
    fi
fi

# gateway_state.json: declare the gateway's INITIAL supervised state on a
# fresh volume. Same first-boot-only env-seed pattern as auth.json above.
#
# On a blank volume there is no gateway_state.json, so the boot reconciler
# (cont-init.d/02-reconcile-profiles → container_boot.reconcile_profile_gateways)
# registers the gateway-default s6 slot but leaves it DOWN — it only
# auto-starts when the last recorded state was "running". That means a
# freshly-provisioned container comes up with the gateway down until
# someone starts it (e.g. from the dashboard). An orchestrator that
# provisions a fresh volume and wants the gateway running from first boot
# can set QWERTY_GATEWAY_BOOTSTRAP_STATE=running; we seed the state file
# here, BEFORE 02-reconcile-profiles runs (cont-init.d scripts run in
# lexicographic order), so the reconciler sees prior_state=running and
# brings the supervised slot up on the very first boot.
#
# This is a generic container contract, not specific to any host: it seeds
# the SAME gateway_state.json the reconciler already consults, exactly as
# QWERTY_AUTH_JSON_BOOTSTRAP seeds auth.json. The [ ! -f ] guard is the
# load-bearing part — on every subsequent boot the persisted state wins,
# so a gateway the operator deliberately stopped stays stopped across
# restarts and we never clobber real runtime state.
#
# Only a literal "running" is honoured (the sole value in the reconciler's
# _AUTOSTART_STATES); any other value is ignored so a typo can't write a
# bogus state the reconciler would treat as "no prior state" anyway.
if [ ! -f "$QWERTY_HOME/gateway_state.json" ] && \
        [ "${QWERTY_GATEWAY_BOOTSTRAP_STATE:-}" = "running" ]; then
    if refuse_symlinked_path "seed" "$QWERTY_HOME/gateway_state.json"; then
        :
    else
        printf '{"gateway_state":"running"}\n' > "$QWERTY_HOME/gateway_state.json"
        chown qwerty:qwerty "$QWERTY_HOME/gateway_state.json" 2>/dev/null || true
        chmod 644 "$QWERTY_HOME/gateway_state.json"
    fi
fi

# --- Sync bundled skills ---
# Invoke the venv's python by absolute path so we don't need a `sh -c`
# wrapper to source the activate script. This is safe because
# skills_sync.py doesn't depend on any environment exports beyond what
# the python binary's own bin-stub already sets up (sys.path is rooted
# at the venv's site-packages by virtue of running .venv/bin/python).
if [ -d "$INSTALL_DIR/skills" ]; then
    as_qwerty "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/tools/skills_sync.py" \
        || echo "[stage2] Warning: skills_sync.py failed; continuing"
fi

# --- Discover agent-browser's Chromium binary ---
# The image's Dockerfile runs `npx playwright install chromium`, which
# populates ``$PLAYWRIGHT_BROWSERS_PATH`` (=/opt/qwerty/.playwright) with
# a ``chromium_headless_shell-<build>/chrome-headless-shell-linux64/``
# directory. agent-browser (the runtime CLI Qwerty spawns for the
# browser tool) doesn't recognise this layout in its own cache scan and
# fails with "Auto-launch failed: Chrome not found" — even though the
# binary is right there (#15697).
#
# Fix: locate the binary at boot and export ``AGENT_BROWSER_EXECUTABLE_PATH``
# via /run/s6/container_environment so the `with-contenv` shebang on
# main-wrapper.sh propagates it into the supervised ``qwerty`` process
# and thence to agent-browser subprocesses.
#
# - Skipped when the user has already set ``AGENT_BROWSER_EXECUTABLE_PATH``
#   (lets users override with a system Chrome install).
# - Filename-matched (not path-matched): the chromium dir contains many
#   shared libraries (libGLESv2.so, libEGL.so, ...) which inherit the
#   executable bit from Playwright's tarball but are NOT browser binaries.
#   We only accept files whose basename is chrome / chromium /
#   chrome-headless-shell / headless_shell / chromium-browser. Compare
#   PR #18635's earlier ``find | grep -Ei 'chrome|chromium'`` which would
#   match the path ``.../chrome-headless-shell-linux64/libGLESv2.so`` and
#   pick a .so.
# - Quietly skipped when $PLAYWRIGHT_BROWSERS_PATH doesn't exist (e.g.
#   custom builds that strip Playwright).
if [ -z "${AGENT_BROWSER_EXECUTABLE_PATH:-}" ] && \
        [ -n "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && \
        [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    browser_bin=$(find "$PLAYWRIGHT_BROWSERS_PATH" -type f -executable \
        \( -name 'chrome' -o -name 'chromium' \
           -o -name 'chrome-headless-shell' -o -name 'headless_shell' \
           -o -name 'chromium-browser' \) \
        2>/dev/null | head -n 1)
    if [ -n "$browser_bin" ]; then
        echo "[stage2] Found agent-browser Chromium binary: $browser_bin"
        # Write to s6's container_environment so with-contenv picks it
        # up for all supervised services (main-qwerty, dashboard, etc.).
        # Idempotent: each boot overwrites with the current path.
        # Some container runtimes / s6-overlay versions do not create the
        # envdir before cont-init hooks run, so create it defensively.
        mkdir -p /run/s6/container_environment
        printf '%s' "$browser_bin" > /run/s6/container_environment/AGENT_BROWSER_EXECUTABLE_PATH
    else
        echo "[stage2] Warning: no Chromium binary under $PLAYWRIGHT_BROWSERS_PATH; browser tool may fail"
    fi
fi

echo "[stage2] Setup complete; starting user services"
