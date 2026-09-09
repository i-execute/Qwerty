"""``--cron-job`` filter wiring for sessions prune/archive/export.

``build_prune_filters`` must map ``args.cron_job`` into the filter dict, and
``SessionDB._prune_filter_where`` must turn it into the same id-prefix range
``list_cron_job_runs`` uses (exact job) or ``source='cron'`` (``all``), so a
user can bulk-delete one recurring job's accumulated run sessions:
``hermes sessions prune --cron-job 5ee599d09fe1``.
"""

from types import SimpleNamespace

import pytest

from hermes_cli.session_filters import build_prune_filters, describe_filters
from hermes_state import SessionDB


@pytest.fixture()
def db(tmp_path):
    """Create a SessionDB with a temp database file."""
    db_path = tmp_path / "test_state.db"
    session_db = SessionDB(db_path=db_path)
    yield session_db
    session_db.close()


def _args(**kwargs):
    base = dict(
        older_than=None,
        newer_than=None,
        before=None,
        after=None,
        source=None,
        cron_job=None,
        title=None,
        end_reason=None,
        cwd=None,
        min_messages=None,
        max_messages=None,
        model=None,
        provider=None,
        user=None,
        chat_id=None,
        chat_type=None,
        branch=None,
        min_tokens=None,
        max_tokens=None,
        min_cost=None,
        max_cost=None,
        min_tool_calls=None,
        max_tool_calls=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_cron_job_maps_into_filters():
    filters = build_prune_filters(_args(cron_job="5ee599d09fe1"))
    assert filters["cron_job"] == "5ee599d09fe1"
    # No time bounds given: older_than_days=None means no implicit 90d cap.
    assert filters["older_than_days"] is None


def test_cron_job_absent_stays_none():
    filters = build_prune_filters(_args())
    assert filters["cron_job"] is None


def test_describe_filters_names_exact_job():
    filters = build_prune_filters(_args(cron_job="5ee599d09fe1"))
    assert "cron job '5ee599d09fe1'" in describe_filters(filters)


def test_describe_filters_names_all_sentinel():
    filters = build_prune_filters(_args(cron_job="all"))
    assert "all cron jobs" in describe_filters(filters)


def test_where_clause_scopes_to_exact_job(db):
    base = 1_700_000_000.0
    for i in range(3):
        db.create_session(session_id=f"cron_alpha_{i:08d}", source="cron")
        db._conn.execute(
            "UPDATE sessions SET started_at = ? WHERE id = ?",
            (base + i * 60, f"cron_alpha_{i:08d}"),
        )
    db.create_session(session_id="cron_xalpha_00000000", source="cron")
    db._conn.execute(
        "UPDATE sessions SET started_at = ? WHERE id = ?",
        (base + 300, "cron_xalpha_00000000"),
    )
    db._conn.execute(
        "UPDATE sessions SET ended_at = ? WHERE source = 'cron'",
        (base + 400,),
    )
    db._conn.commit()

    candidates = db.list_prune_candidates(cron_job="alpha")

    assert {c["id"] for c in candidates} == {
        "cron_alpha_00000000",
        "cron_alpha_00000001",
        "cron_alpha_00000002",
    }


def test_where_clause_all_sentinel_matches_every_cron_source(db):
    base = 1_700_000_000.0
    db.create_session(session_id="cron_alpha_00000000", source="cron")
    db.create_session(session_id="cron_beta_00000000", source="cron")
    db.create_session(session_id="cli_alpha_00000000", source="cli")
    db._conn.execute(
        "UPDATE sessions SET ended_at = ? WHERE id IN "
        "('cron_alpha_00000000', 'cron_beta_00000000', 'cli_alpha_00000000')",
        (base + 400,),
    )
    db._conn.commit()

    candidates = db.list_prune_candidates(cron_job="all")

    assert {c["id"] for c in candidates} == {
        "cron_alpha_00000000",
        "cron_beta_00000000",
    }
