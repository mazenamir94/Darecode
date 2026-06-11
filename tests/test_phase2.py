"""
Phase 2 tests for DareCode v2.0 — settings, server manager, project manager.

Runs without Bedrock credentials. All filesystem work happens inside
tempfile.TemporaryDirectory so the suite is fully isolated.

Run from agent2\\wiki:
    python -m pytest tests/test_phase2.py -v
    (or) python -m unittest tests.test_phase2 -v
"""

import json
import os
import socket
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Make `core.*` importable regardless of how the suite is launched.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings import Settings, apply_settings                      # noqa: E402
from core.server_manager import ServerManager, find_free_port, is_port_in_use  # noqa: E402
from core.project_manager import ProjectManager                          # noqa: E402

SLEEPER = f'"{sys.executable}" -c "import time; time.sleep(60)"'


def _wait_dead(proc, timeout=8.0) -> bool:
    """Poll a Popen handle until it exits or timeout. Returns True if dead."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return True
        time.sleep(0.1)
    return proc.poll() is not None


# ── core/settings.py ─────────────────────────────────────────────────────────
class TestSettings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_loads_defaults(self):
        s = Settings(self.dir)
        self.assertFalse(s.get("defenders_auto"))
        self.assertTrue(s.get("harness_enabled"))

    def test_set_save_reload_persists(self):
        s = Settings(self.dir)
        s.set("model", "test-model-x")
        s.set("defenders_auto", True)
        s.set("harness_enabled", False)

        s2 = Settings(self.dir)
        self.assertEqual(s2.get("model"), "test-model-x")
        self.assertTrue(s2.get("defenders_auto"))
        self.assertFalse(s2.get("harness_enabled"))

    def test_api_key_never_written(self):
        s = Settings(self.dir)
        for key in ("api_key", "bedrock_api_key", "aws_secret", "auth_token"):
            s.set(key, "super-secret-123")
        text = (self.dir / "config.json").read_text(encoding="utf-8")
        self.assertNotIn("super-secret-123", text)
        # And a hand-edited secret in the file is ignored on load.
        data = json.loads(text)
        data["sneaky_api_key"] = "leaked-456"
        (self.dir / "config.json").write_text(json.dumps(data), encoding="utf-8")
        s3 = Settings(self.dir)
        self.assertIsNone(s3.get("sneaky_api_key"))

    def test_default_config_dir_is_project_local_in_container(self):
        # Inside Docker (/.dockerenv exists), config must live in the bind-mounted
        # repo (./.darecode) — ~/.darecode dies with `docker compose run --rm`.
        from unittest.mock import patch
        from core.settings import _default_config_dir
        with patch("core.settings.os.path.exists", return_value=True):
            self.assertEqual(_default_config_dir(), Path(".darecode"))
        with patch("core.settings.os.path.exists", return_value=False):
            self.assertEqual(_default_config_dir(), Path.home() / ".darecode")

    @unittest.skipIf(os.name == "nt", "chmod not meaningful on Windows")
    def test_chmod_600_after_save(self):
        s = Settings(self.dir)
        s.set("model", "m")
        mode = (self.dir / "config.json").stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)


# ── core/server_manager.py ───────────────────────────────────────────────────
class TestServerManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.cwd = Path(self.tmp.name)
        self.sm = ServerManager()

    def tearDown(self):
        self.sm.stop_all()
        # Give Windows a beat to release handles before temp cleanup.
        time.sleep(0.3)
        self.tmp.cleanup()

    def test_find_free_port_is_bindable(self):
        port = find_free_port(5000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))  # raises OSError if not actually free

    def test_is_port_in_use(self):
        port = find_free_port(5000)
        self.assertFalse(is_port_in_use(port))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            s.listen(1)
            self.assertTrue(is_port_in_use(port))
        self.assertFalse(is_port_in_use(port))

    def test_start_returns_running_with_pid(self):
        result = self.sm.start("alpha", SLEEPER, cwd=self.cwd, port=find_free_port(5000))
        self.assertEqual(result["status"], "running")
        self.assertIsInstance(result["pid"], int)
        self.assertGreater(result["pid"], 0)

    def test_stop_kills_process(self):
        self.sm.start("alpha", SLEEPER, cwd=self.cwd, port=find_free_port(5000))
        proc = self.sm._servers["alpha"].process  # capture handle before stop pops it
        result = self.sm.stop("alpha")
        self.assertEqual(result["status"], "stopped")
        self.assertTrue(_wait_dead(proc), "process still alive after stop()")
        self.assertFalse(self.sm.is_running("alpha"))

    def test_restart_same_name_kills_old_pid(self):
        r1 = self.sm.start("alpha", SLEEPER, cwd=self.cwd, port=5005)
        old_proc = self.sm._servers["alpha"].process
        r2 = self.sm.start("alpha", SLEEPER, cwd=self.cwd, port=5005)
        self.assertEqual(r2["status"], "running")
        self.assertNotEqual(r1["pid"], r2["pid"])
        self.assertTrue(_wait_dead(old_proc), "old process survived the restart")

    def test_two_names_get_distinct_ports(self):
        ra = self.sm.start("alpha", SLEEPER, cwd=self.cwd, port=5000)
        rb = self.sm.start("beta", SLEEPER, cwd=self.cwd, port=5000)
        self.assertEqual(ra["status"], "running")
        self.assertEqual(rb["status"], "running")
        self.assertIsNotNone(ra["port"])
        self.assertIsNotNone(rb["port"])
        self.assertNotEqual(ra["port"], rb["port"], "port collision between two servers")

    def test_list_servers_empty_on_fresh_manager(self):
        self.assertEqual(ServerManager().list_servers(), [])

    def test_stop_nonexistent(self):
        self.assertEqual(self.sm.stop("nonexistent")["status"], "not_found")

    def test_reap_dead_removes_exited_server(self):
        quick = f'"{sys.executable}" -c "pass"'  # exits immediately
        self.sm.start("ghost", quick, cwd=self.cwd, port=find_free_port(5000))
        proc = self.sm._servers["ghost"].process
        self.assertTrue(_wait_dead(proc), "quick process never exited")
        reaped = self.sm.reap_dead()
        self.assertIn("ghost", reaped)
        self.assertEqual(self.sm.list_servers(), [])

    def test_reap_dead_keeps_running_server(self):
        self.sm.start("alive", SLEEPER, cwd=self.cwd, port=find_free_port(5000))
        self.assertEqual(self.sm.reap_dead(), [])
        self.assertTrue(self.sm.is_running("alive"))


# ── core/project_manager.py ──────────────────────────────────────────────────
class TestProjectManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name) / "workspace"
        self.ws.mkdir()
        self.pm = ProjectManager(self.ws)

    def tearDown(self):
        self.tmp.cleanup()

    def _make_flask_app(self, name="flask_app"):
        d = self.ws / name
        (d / "templates").mkdir(parents=True)
        (d / "app.py").write_text(
            "from flask import Flask\n"
            "app = Flask(__name__)\n"
            "@app.route('/')\n"
            "def home():\n    return 'hi'\n"
            "app.run(host='0.0.0.0', port=5000)\n",
            encoding="utf-8",
        )
        (d / "templates" / "index.html").write_text("<h1>hi</h1>", encoding="utf-8")
        return d

    def _make_node_app(self, name="node_app"):
        d = self.ws / name
        d.mkdir(parents=True)
        (d / "package.json").write_text(json.dumps({
            "name": name, "main": "server.js",
            "dependencies": {"express": "^4.18.0"},
        }), encoding="utf-8")
        (d / "server.js").write_text(
            "const express = require('express');\n"
            "const app = express();\n"
            "app.listen(5000, '0.0.0.0');\n",
            encoding="utf-8",
        )
        return d

    def test_empty_workspace_has_no_projects(self):
        self.assertEqual(self.pm.list_projects(), [])

    def test_finds_two_projects(self):
        self._make_flask_app()
        self._make_node_app()
        names = {p["name"] for p in self.pm.list_projects()}
        self.assertEqual(names, {"flask_app", "node_app"})

    def test_root_level_files_are_not_projects(self):
        (self.ws / "hello.py").write_text("print('hi')", encoding="utf-8")
        (self.ws / "notes.txt").write_text("scratch", encoding="utf-8")
        self.assertEqual(self.pm.list_projects(), [])

    def test_detects_flask_type(self):
        self._make_flask_app()
        proj = self.pm.list_projects()[0]
        self.assertEqual(proj["type"], "flask")

    def test_detects_express_type(self):
        self._make_node_app()
        proj = self.pm.list_projects()[0]
        self.assertEqual(proj["type"], "express")

    def test_set_current(self):
        self._make_flask_app("proj_a")
        self.assertTrue(self.pm.set_current("proj_a"))
        self.assertEqual(self.pm.current_project, "proj_a")
        self.assertEqual(self.pm.current_project_dir, self.ws / "proj_a")
        self.assertEqual(self.pm.current_project_type, "flask")

    def test_set_current_nonexistent(self):
        self.assertFalse(self.pm.set_current("nonexistent"))
        self.assertIsNone(self.pm.current_project)

    def test_file_count(self):
        self._make_flask_app()  # app.py + templates/index.html = 2 files
        proj = self.pm.list_projects()[0]
        self.assertEqual(proj["file_count"], 2)

    def test_ignored_dirs_are_skipped(self):
        d = self._make_flask_app()
        (d / "__pycache__").mkdir()
        (d / "__pycache__" / "app.cpython-311.pyc").write_bytes(b"\x00")
        (self.ws / "__pycache__").mkdir()
        proj = self.pm.list_projects()
        self.assertEqual({p["name"] for p in proj}, {"flask_app"})
        self.assertEqual(proj[0]["file_count"], 2)


# ── Integration: settings → brain.reconfigure ───────────────────────────────
class TestSettingsBrainIntegration(unittest.TestCase):
    def test_persisted_model_applied_via_reconfigure(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Settings(tmp)
            s.set("model", "eu.anthropic.claude-fable-5-v1", save=False)
            s.set("region", "eu-west-1")  # saves both

            reloaded = Settings(tmp)  # fresh read from disk
            brain = MagicMock()
            apply_settings(brain, reloaded)
            brain.reconfigure.assert_called_once_with(
                model_id="eu.anthropic.claude-fable-5-v1",
                region="eu-west-1",
            )

    def test_no_reconfigure_when_nothing_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = MagicMock()
            apply_settings(brain, Settings(tmp))
            brain.reconfigure.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
