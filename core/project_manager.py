"""
ProjectManager — tracks workspace/ subdirectories as named projects.

Adapted from the old DareCode project_manager: here a "project" is simply an
immediate subdirectory of workspace/ (which is what the PROJECT STRUCTURE RULES
make the agent create). Provides type detection and entry-file/dev-command
helpers that /server uses to launch the right thing.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Directories that are never projects and never counted as project files.
_IGNORED_DIRS = {"__pycache__", "node_modules", ".git", ".venv", "venv"}

WEB_TYPES = {"flask", "fastapi", "express", "node", "static"}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _project_files(project_dir: Path) -> List[Path]:
    files = []
    for p in project_dir.rglob("*"):
        if not p.is_file():
            continue
        if any(part in _IGNORED_DIRS for part in p.parts):
            continue
        files.append(p)
    return files


def detect_project_type(project_dir: Path) -> str:
    """Best-effort stack detection for a project directory.

    Returns one of: flask, fastapi, express, node, python, static, unknown.
    """
    project_dir = Path(project_dir)
    pkg = project_dir / "package.json"
    if pkg.exists():
        content = _read(pkg).lower()
        has_server_js = any(
            (project_dir / n).exists() for n in ("server.js", "app.js", "index.js")
        )
        if "express" in content or has_server_js:
            return "express"
        return "node"

    py_files = [p for p in _project_files(project_dir) if p.suffix == ".py"]
    for p in py_files:
        content = _read(p)
        if "Flask(" in content:
            return "flask"
        if "FastAPI(" in content:
            return "fastapi"
    if py_files:
        return "python"

    if any(p.suffix == ".html" for p in _project_files(project_dir)):
        return "static"

    return "unknown"


def find_entry_file(project_dir: Path, project_type: str) -> Optional[str]:
    """Relative entry filename for a project, or None."""
    project_dir = Path(project_dir)

    if project_type in ("express", "node"):
        pkg = project_dir / "package.json"
        if pkg.exists():
            try:
                data = json.loads(_read(pkg))
                main = data.get("main") or ""
                start = (data.get("scripts") or {}).get("start", "")
                if main and (project_dir / main).exists():
                    return main
                if start.startswith("node "):
                    candidate = start[len("node "):].strip()
                    if (project_dir / candidate).exists():
                        return candidate
            except (json.JSONDecodeError, AttributeError):
                pass
        for name in ("server.js", "app.js", "index.js",
                     "src/server.js", "src/app.js", "src/index.js"):
            if (project_dir / name).exists():
                return name
        return None

    if project_type in ("flask", "fastapi", "python"):
        for name in ("app.py", "main.py", "server.py", "src/app.py", "src/main.py"):
            if (project_dir / name).exists():
                return name
        py = [p for p in _project_files(project_dir) if p.suffix == ".py"]
        if py:
            return str(py[0].relative_to(project_dir)).replace("\\", "/")
        return None

    if project_type == "static":
        for name in ("index.html", "public/index.html"):
            if (project_dir / name).exists():
                return name
    return None


def get_dev_command(project_type: str, entry: Optional[str], port: int) -> Optional[str]:
    """Shell command that runs the project (cwd = the prepared run dir)."""
    if project_type in ("flask", "fastapi", "python") and entry:
        return f'"{sys.executable}" {entry}'
    if project_type in ("express", "node") and entry:
        return f"node {entry}"
    if project_type == "static":
        return f'"{sys.executable}" -m http.server {port} --bind 0.0.0.0'
    return None


class ProjectManager:
    """Lists and activates workspace/<name>/ projects."""

    def __init__(self, workspace_dir):
        self.workspace_dir = Path(workspace_dir)
        self._current_project: Optional[str] = None
        self._current_project_dir: Optional[Path] = None
        self._current_project_type: Optional[str] = None

    # ── Introspection ──────────────────────────────────────────────────
    def list_projects(self) -> List[Dict]:
        projects = []
        if not self.workspace_dir.exists():
            return projects
        for d in sorted(self.workspace_dir.iterdir()):
            if not d.is_dir() or d.name in _IGNORED_DIRS:
                continue
            files = _project_files(d)
            projects.append({
                "name": d.name,
                "path": str(d),
                "type": detect_project_type(d),
                "file_count": len(files),
            })
        return projects

    @property
    def current_project(self) -> Optional[str]:
        return self._current_project

    @property
    def current_project_dir(self) -> Optional[Path]:
        return self._current_project_dir

    @property
    def current_project_type(self) -> Optional[str]:
        return self._current_project_type

    # ── Activation ─────────────────────────────────────────────────────
    def set_current(self, name: str) -> bool:
        project_dir = self.workspace_dir / name
        if project_dir.exists() and project_dir.is_dir():
            self._current_project = name
            self._current_project_dir = project_dir
            self._current_project_type = detect_project_type(project_dir)
            return True
        return False
