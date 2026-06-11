"""
Persistent, non-secret settings for DareCode at ~/.darecode/config.json.

Secrets (the Bedrock API key) stay in .env — this layer REFUSES to persist any
key that looks like a credential, even if asked to. Settings changed at runtime
(/model, /change api region+model, /team, /harness) survive restarts.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

DEFAULTS = {
    "model": None,            # None -> keep the .env/config.py default
    "region": None,
    "defenders_auto": False,  # /team off by default; explicit /defenders is more reliable
    "harness_enabled": True,
    "harness_summary": True,
}

# Any key matching this is silently dropped on save AND ignored on load.
_SECRET_KEY_RE = re.compile(r"(api[_-]?key|secret|token|password|bearer)", re.IGNORECASE)


def _default_config_dir() -> Path:
    # Inside a container, $HOME dies with the container (docker compose run --rm),
    # so ~/.darecode would lose settings on every restart. The app's cwd (/app) is
    # the bind-mounted repo — a project-local .darecode/ survives there. On the
    # host, keep the conventional ~/.darecode.
    if os.path.exists("/.dockerenv"):
        return Path(".darecode")
    return Path.home() / ".darecode"


class Settings:
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = Path(config_dir) if config_dir else _default_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if not self.config_file.exists():
            return
        try:
            stored = json.loads(self.config_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if isinstance(stored, dict):
            for k, v in stored.items():
                if not _SECRET_KEY_RE.search(str(k)):
                    self._data[k] = v

    def get(self, key: str, default=None):
        value = self._data.get(key, default)
        return default if value is None else value

    def set(self, key: str, value, save: bool = True):
        self._data[key] = value
        if save:
            self.save()

    def save(self):
        out = {
            k: v for k, v in self._data.items()
            if v is not None and not _SECRET_KEY_RE.search(str(k))
        }
        self.config_file.write_text(json.dumps(out, indent=2), encoding="utf-8")
        try:
            self.config_file.chmod(0o600)
        except OSError:
            pass  # not supported on Windows


def apply_settings(brain, settings: Settings) -> None:
    """Push persisted model/region onto a Brain at startup (no-op if unset)."""
    kwargs = {}
    model = settings.get("model")
    region = settings.get("region")
    if model:
        kwargs["model_id"] = model
    if region:
        kwargs["region"] = region
    if kwargs:
        brain.reconfigure(**kwargs)
