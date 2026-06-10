"""
DareCode harness — deep agent observability.

Records every meaningful step the agent takes (LLM calls, tool executions, the
run lifecycle) with timestamps, durations, parent/child nesting, and truncated,
secret-scrubbed payloads. This is the data behind `/harness show`, the post-run
summary panel, and `/stats`.

Off-switchable via `/harness off`. Cheap when idle.

Design notes (carried over from the original trace harness):
    - Parent-span tracking uses `contextvars` so concurrent threads don't clobber
      each other's parent pointer.
    - Payload scrubbing for secrets (e.g. the Bearer token) is LAZY: applied at
      save/display time only, so the hot path stays regex-free.
    - The in-memory run buffer is a `deque(maxlen=N)` — auto-evicts the oldest run.
"""

from __future__ import annotations

import json
import re
import time
from collections import deque
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Iterable, Optional

# Per-thread parent-span tracker. Each contextvar copy is isolated.
_current_parent: ContextVar[Optional[int]] = ContextVar("darecode_harness_parent", default=None)

# Payload truncation bound (memory cap, not security).
_MAX_STRING_LEN = 2000

# Scrub patterns applied lazily at save/display time.
_SECRET_KEY_PATTERNS = [
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"authorization", re.IGNORECASE),
    re.compile(r"bearer", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
]
_SECRET_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"Bearer\s+\S+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


@dataclass
class HarnessEvent:
    id: int
    parent_id: Optional[int]
    category: str          # agent | llm | tool
    name: str
    status: str            # start | ok | error
    ts: float              # epoch seconds
    duration_ms: Optional[float] = None
    payload: dict = field(default_factory=dict)


@dataclass
class HarnessRun:
    id: int
    started_at: float
    user_message: str
    events: list = field(default_factory=list)
    ended_at: Optional[float] = None
    status: str = "running"   # running | ok | error

    @property
    def duration_ms(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000.0


def _truncate(value: Any) -> Any:
    """Cap string size at insertion time. Bounded memory, not security."""
    if isinstance(value, str):
        if len(value) > _MAX_STRING_LEN:
            return value[:_MAX_STRING_LEN] + f"…({len(value) - _MAX_STRING_LEN} more chars)"
        return value
    if isinstance(value, dict):
        return {k: _truncate(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_truncate(v) for v in value]
    return value


def _scrub_value(value: Any) -> Any:
    if isinstance(value, str):
        scrubbed = value
        for pat in _SECRET_VALUE_PATTERNS:
            scrubbed = pat.sub("***", scrubbed)
        return scrubbed
    return value


def scrub(payload: Any) -> Any:
    """Lazy secret scrubbing — call ONLY at save/display time, not on insert."""
    if isinstance(payload, dict):
        out = {}
        for k, v in payload.items():
            if any(p.search(str(k)) for p in _SECRET_KEY_PATTERNS):
                out[k] = "***"
            else:
                out[k] = scrub(v)
        return out
    if isinstance(payload, list):
        return [scrub(v) for v in payload]
    return _scrub_value(payload)


class Harness:
    """Collector for agent observability. Use the module-level `harness` instance."""

    def __init__(self):
        self.enabled: bool = True
        self.persist: bool = True
        self.summary: bool = True
        self.runs: deque[HarnessRun] = deque(maxlen=20)
        self._lock = Lock()
        self._next_event_id = 1
        self._next_run_id = 1
        self._active_run: Optional[HarnessRun] = None
        self._save_dirs: list[Path] = []

    # ── Configuration ──────────────────────────────────────────────────
    def configure(self, *, enabled: bool, persist: bool, summary: bool,
                  max_runs: int, save_dirs: Iterable[Path]):
        self.enabled = bool(enabled)
        self.persist = bool(persist)
        self.summary = bool(summary)
        if max_runs and max_runs > 0 and max_runs != self.runs.maxlen:
            self.runs = deque(self.runs, maxlen=int(max_runs))
        self._save_dirs = [Path(p) for p in save_dirs]

    def set_enabled(self, value: bool):
        self.enabled = bool(value)

    # ── Run lifecycle ──────────────────────────────────────────────────
    def start_run(self, user_message: str) -> Optional[HarnessRun]:
        if not self.enabled:
            return None
        with self._lock:
            run = HarnessRun(
                id=self._next_run_id,
                started_at=time.time(),
                user_message=user_message[:200],
            )
            self._next_run_id += 1
            self._active_run = run
            self.runs.append(run)
            return run

    def end_run(self, status: str = "ok"):
        if not self.enabled or self._active_run is None:
            return
        with self._lock:
            self._active_run.ended_at = time.time()
            self._active_run.status = status
            self._active_run = None

    def last_run(self) -> Optional[HarnessRun]:
        if self.runs:
            return self.runs[-1]
        return None

    def get_run(self, run_id: int) -> Optional[HarnessRun]:
        for r in self.runs:
            if r.id == run_id:
                return r
        return None

    def clear(self):
        with self._lock:
            self.runs.clear()
            self._active_run = None

    # ── Event recording ────────────────────────────────────────────────
    def _record(self, category: str, name: str, status: str, payload: dict,
                duration_ms: Optional[float] = None,
                parent_id: Optional[int] = None) -> HarnessEvent:
        with self._lock:
            eid = self._next_event_id
            self._next_event_id += 1
            evt = HarnessEvent(
                id=eid,
                parent_id=parent_id if parent_id is not None else _current_parent.get(),
                category=category,
                name=name,
                status=status,
                ts=time.time(),
                duration_ms=duration_ms,
                payload=_truncate(payload),
            )
            if self._active_run is not None:
                self._active_run.events.append(evt)
            else:
                # Stray event before any run started — create an implicit run.
                implicit = HarnessRun(
                    id=self._next_run_id,
                    started_at=evt.ts,
                    user_message="(no active run)",
                )
                self._next_run_id += 1
                implicit.events.append(evt)
                self.runs.append(implicit)
            return evt

    def event(self, category: str, name: str, duration_ms: Optional[float] = None, **payload):
        if not self.enabled:
            return
        self._record(category, name, "ok", payload, duration_ms=duration_ms)

    @contextmanager
    def span(self, category: str, name: str, **payload):
        if not self.enabled:
            yield _NullSpan()
            return

        start = time.perf_counter()
        evt = self._record(category, name, "start", dict(payload))
        token = _current_parent.set(evt.id)
        handle = _SpanHandle(evt)
        try:
            yield handle
        except BaseException as e:
            evt.payload = _truncate({**handle._payload, "error": f"{type(e).__name__}: {e}"})
            evt.duration_ms = (time.perf_counter() - start) * 1000.0
            evt.status = "error"
            raise
        else:
            evt.payload = _truncate(handle._payload)
            evt.duration_ms = (time.perf_counter() - start) * 1000.0
            evt.status = handle._status
        finally:
            _current_parent.reset(token)

    # ── Persistence ────────────────────────────────────────────────────
    def save_run(self, run: Optional[HarnessRun] = None) -> list[Path]:
        run = run or self.last_run()
        if run is None or not self._save_dirs:
            return []
        stamp = datetime.fromtimestamp(run.started_at).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{stamp}_run{run.id}.jsonl"
        written = []
        for d in self._save_dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
                path = d / filename
                with path.open("w", encoding="utf-8") as f:
                    header = {
                        "_type": "run_header",
                        "run_id": run.id,
                        "started_at": run.started_at,
                        "ended_at": run.ended_at,
                        "duration_ms": run.duration_ms,
                        "status": run.status,
                        "user_message": run.user_message,
                    }
                    f.write(json.dumps(scrub(header)) + "\n")
                    for evt in run.events:
                        line = asdict(evt)
                        line["payload"] = scrub(line["payload"])
                        f.write(json.dumps(line) + "\n")
                written.append(path)
                self._prune_dir(d)
            except OSError:
                continue
        return written

    def _prune_dir(self, directory: Path):
        """Keep only the newest `runs.maxlen` harness files so disk stays bounded."""
        keep = self.runs.maxlen or 20
        try:
            files = sorted(
                directory.glob("*_run*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for stale in files[keep:]:
                try:
                    stale.unlink()
                except OSError:
                    pass
        except OSError:
            pass


class _SpanHandle:
    """Returned by `harness.span(...)`; allows mid-span payload updates."""
    def __init__(self, evt: HarnessEvent):
        self._evt = evt
        self._payload = dict(evt.payload)
        self._status = "ok"

    def set(self, **kwargs):
        self._payload.update(kwargs)

    def mark_error(self):
        self._status = "error"


class _NullSpan:
    """No-op span returned when the harness is disabled."""
    def set(self, **kwargs):
        pass

    def mark_error(self):
        pass


# Module-level singleton.
harness = Harness()


def init(*, enabled: bool = True, persist: bool = True, summary: bool = True,
         max_runs: int = 20, save_dirs: Optional[Iterable[Path]] = None) -> Harness:
    """Wire the harness on startup. Called once from main.py."""
    if save_dirs is None:
        save_dirs = [Path(__file__).resolve().parent.parent / "harnesses"]
    harness.configure(enabled=enabled, persist=persist, summary=summary,
                      max_runs=max_runs, save_dirs=save_dirs)
    return harness


def summarize_run(run: Optional[HarnessRun]) -> dict:
    """Walk a run's events into a compact summary for the post-run panel.

    Returns: status, duration_ms, steps, llm_calls, total_tokens, tools
    (name->count), tool_calls, errors, and an ordered `timeline`.
    """
    summary = {
        "status": "ok",
        "duration_ms": None,
        "steps": 0,
        "llm_calls": 0,
        "total_tokens": 0,
        "tools": {},
        "tool_calls": 0,
        "errors": [],
        "timeline": [],
    }
    if run is None:
        summary["status"] = "empty"
        return summary

    summary["status"] = run.status
    summary["duration_ms"] = run.duration_ms
    summary["steps"] = len(run.events)

    for evt in run.events:
        cat, name = evt.category, evt.name
        payload = evt.payload or {}

        is_err = (
            evt.status == "error"
            or name == "error"
            or payload.get("status") == "error"
            or bool(payload.get("error"))
        )
        if is_err:
            msg = payload.get("error") or f"{cat}/{name} failed"
            summary["errors"].append(f"{cat}/{name}: {msg}")

        label = None
        tokens = None
        if cat == "llm" and name == "call":
            summary["llm_calls"] += 1
            tok = payload.get("total_tokens")
            if isinstance(tok, (int, float)):
                summary["total_tokens"] += int(tok)
                tokens = int(tok)
            model = payload.get("model", "llm")
            label = f"LLM call ({model})"
        elif cat == "llm" and name == "error":
            label = f"LLM error ({payload.get('model', 'llm')})"
        elif cat == "tool":
            summary["tools"][name] = summary["tools"].get(name, 0) + 1
            summary["tool_calls"] += 1
            label = f"Tool · {name}"
        elif cat == "agent" and name == "run" and is_err:
            label = "Agent run"

        if label is not None:
            summary["timeline"].append({
                "label": label,
                "category": cat,
                "status": "error" if is_err else "ok",
                "duration_ms": evt.duration_ms,
                "tokens": tokens,
                "error": (payload.get("error") if is_err else None),
            })

    return summary
