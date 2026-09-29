"""``_apply_cron_session_retention`` — the automatic cron run-session trim.

A recurring cron job creates one persistent session per execution
(``cron_{job_id}_{timestamp}``). Without retention, a 15-minute watchdog
accumulates thousands of session rows forever. The helper runs after every
job execution and trims that job's runs down to ``cron.session_retention``
(default 50) in config.yaml.
"""

from cron.scheduler import _apply_cron_session_retention
from hermes_state import SessionDB


def _seed_runs(db, job_id, count, base=1_700_000_000.0):
    for i in range(count):
        sid = f"cron_{job_id}_{i:08d}"
        db.create_session(session_id=sid, source="cron")
        db.append_message(sid, role="user", content=f"run {i}")
        db.end_session(sid, "cron_complete")
        db._conn.execute(
            "UPDATE sessions SET started_at = ? WHERE id = ?",
            (base + i * 60, sid),
        )
    db._conn.commit()


def _open_db(home):
    return SessionDB(db_path=home / "state.db")


class TestApplyCronSessionRetention:
    def test_trims_to_configured_window(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: 5\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 12)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_alpha_%'"
        ).fetchone()[0] == 5
        db.close()

    def test_default_retention_50_without_config(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 55)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_alpha_%'"
        ).fetchone()[0] == 50
        db.close()

    def test_null_retention_disables_trimming(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: null\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 60)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_alpha_%'"
        ).fetchone()[0] == 60
        db.close()

    def test_all_string_disables_trimming(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: all\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 60)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_alpha_%'"
        ).fetchone()[0] == 60
        db.close()

    def test_keeps_newest_runs_only(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: 3\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 8)

        _apply_cron_session_retention(db, "alpha")

        remaining = [
            r["id"]
            for r in db._conn.execute(
                "SELECT id FROM sessions WHERE id LIKE 'cron_alpha_%' "
                "ORDER BY started_at DESC"
            ).fetchall()
        ]
        assert remaining == [
            "cron_alpha_00000007",
            "cron_alpha_00000006",
            "cron_alpha_00000005",
        ]
        db.close()

    def test_other_jobs_untouched(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: 3\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 8)
        _seed_runs(db, "beta", 8)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_beta_%'"
        ).fetchone()[0] == 8
        db.close()

    def test_no_runs_is_noop(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: 3\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)

        _apply_cron_session_retention(db, "ghost")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE source = 'cron'"
        ).fetchone()[0] == 0
        db.close()

    def test_invalid_retention_value_never_raises(self, tmp_path, monkeypatch):
        home = tmp_path / "hermes_home"
        home.mkdir()
        (home / "config.yaml").write_text(
            "cron:\n  session_retention: bananas\n", encoding="utf-8"
        )
        monkeypatch.setattr("cron.scheduler._hermes_home", home)
        db = _open_db(home)
        _seed_runs(db, "alpha", 8)

        _apply_cron_session_retention(db, "alpha")

        assert db._conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE id LIKE 'cron_alpha_%'"
        ).fetchone()[0] == 8
        db.close()
