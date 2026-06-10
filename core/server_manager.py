"""
ServerManager — background web-server lifecycle for DareCode.

Ported from the old DareCode server_manager with hardening:
  - allocate_port() also excludes ports held by TRACKED running servers, not just
    OS-bound ones — so two or three web apps coexist on distinct ports even
    before each app has actually bound its socket.
  - Restarting the same name kills the previous process tree first and waits for
    the OS to release the socket (fixes the port-5000 collision and process leak).
  - Browser opening is container-aware (no-op inside Docker; the UI prints the URL).

Ports stay inside the compose-published range 5000-5005 by default.
"""

import subprocess
import threading
import platform
import atexit
import os
import re
import socket
import time
import webbrowser
from typing import Dict, List, Optional
from dataclasses import dataclass, field

PORT_RANGE_START = 5000
PORT_RANGE_LEN = 6  # 5000-5005 published in docker-compose.yml

IS_WINDOWS = platform.system() == "Windows"


# ── Port utilities ───────────────────────────────────────────────────────────
def is_port_in_use(port: int) -> bool:
    """True if `port` cannot be bound on 0.0.0.0 (something is holding it)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True


def find_free_port(start: int, limit: int = PORT_RANGE_LEN) -> int:
    """First free port at or after `start`; falls back to `start` if none found."""
    for candidate in range(start, start + max(1, limit)):
        if not is_port_in_use(candidate):
            return candidate
    return start


def wait_for_port_release(port: int, timeout: float = 3.0) -> bool:
    """Poll until `port` is free (after killing a server) or timeout. Best-effort."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_port_in_use(port):
            return True
        time.sleep(0.1)
    return False


# Patterns to detect a port from server stdout
PORT_PATTERNS = [
    re.compile(r'Local:\s+https?://(?:localhost|[\d.]+):(\d+)', re.IGNORECASE),
    re.compile(r'listening\s+(?:on\s+)?(?:port\s+)?(\d+)', re.IGNORECASE),
    re.compile(r'(?:started|running)\s+(?:on|at)\s+(?:port\s+)?(\d+)', re.IGNORECASE),
    re.compile(r'localhost:(\d+)', re.IGNORECASE),
    re.compile(r'https?://[\w.]+:(\d+)', re.IGNORECASE),
    re.compile(r'port\s+(\d+)', re.IGNORECASE),
]


@dataclass
class ServerProcess:
    """Tracks a running dev server."""
    name: str
    pid: int
    port: Optional[int]
    url: Optional[str]
    command: str
    cwd: str
    process: subprocess.Popen
    _reader_thread: Optional[threading.Thread] = field(default=None, repr=False)
    _output_lines: List[str] = field(default_factory=list, repr=False)
    _port_event: threading.Event = field(default_factory=threading.Event, repr=False)


class ServerManager:
    """Manages background web-server processes."""

    def __init__(self):
        self._servers: Dict[str, ServerProcess] = {}
        self._lock = threading.Lock()
        atexit.register(self.stop_all)

    # ── Port allocation (multi-app safe) ───────────────────────────────
    def allocate_port(self, requested: Optional[int] = None) -> int:
        """Pick a port that is free at the OS level AND not held by any tracked
        running server. Scans the published range starting at `requested`."""
        with self._lock:
            taken = {
                s.port for s in self._servers.values()
                if s.port is not None and s.process.poll() is None
            }
        candidates = []
        if requested is not None:
            candidates.append(requested)
        candidates += list(range(PORT_RANGE_START, PORT_RANGE_START + PORT_RANGE_LEN))
        for port in candidates:
            if port in taken:
                continue
            if is_port_in_use(port):
                continue
            return port
        return requested if requested is not None else PORT_RANGE_START

    # ── Lifecycle ──────────────────────────────────────────────────────
    def start(
        self,
        name: str,
        command: str,
        cwd,
        port: Optional[int] = None,
        wait_for_port: float = 15.0,
    ) -> Dict:
        """Start a server as a background process.

        Returns {"name", "pid", "port", "url", "status", "error"}.
        If a server with the same name is running, it is killed first (and its
        socket awaited) before the new one starts.
        """
        old_port = None
        with self._lock:
            if name in self._servers:
                old_port = self._servers[name].port
                self._stop_one(name)

        # Let the OS release the old socket before rebinding the same port.
        if old_port:
            wait_for_port_release(old_port, timeout=3.0)

        # If an explicit port was requested but is unavailable, shift to a safe one.
        if port is not None and (is_port_in_use(port) or self._port_tracked(port)):
            port = self.allocate_port(port)

        try:
            kwargs = {
                "shell": True,
                "cwd": str(cwd),
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "bufsize": 1,
            }
            if IS_WINDOWS:
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            # Pass the chosen port via env so frameworks that honor PORT bind it.
            if port is not None:
                kwargs["env"] = {**os.environ, "PORT": str(port)}

            proc = subprocess.Popen(command, **kwargs)

            server = ServerProcess(
                name=name,
                pid=proc.pid,
                port=port,
                url=f"http://localhost:{port}" if port else None,
                command=command,
                cwd=str(cwd),
                process=proc,
            )

            reader = threading.Thread(
                target=self._read_output,
                args=(server,),
                daemon=True,
                name=f"server-{name}-reader",
            )
            server._reader_thread = reader
            reader.start()

            with self._lock:
                self._servers[name] = server

            # Wait for stdout port detection only when we don't know the port.
            if port is None:
                server._port_event.wait(timeout=wait_for_port)
                if proc.poll() is not None:
                    output = "\n".join(server._output_lines[-20:])
                    with self._lock:
                        self._servers.pop(name, None)
                    return {
                        "name": name, "pid": None, "port": None, "url": None,
                        "status": "failed",
                        "error": f"Server exited (code {proc.returncode}):\n{output}",
                    }

            return {
                "name": name,
                "pid": proc.pid,
                "port": server.port,
                "url": server.url,
                "status": "running",
                "error": None,
            }

        except FileNotFoundError:
            return {
                "name": name, "pid": None, "port": None, "url": None,
                "status": "failed",
                "error": f"Command not found: {command.split()[0]}",
            }
        except Exception as e:
            return {
                "name": name, "pid": None, "port": None, "url": None,
                "status": "failed", "error": str(e),
            }

    def _port_tracked(self, port: int) -> bool:
        with self._lock:
            return any(
                s.port == port and s.process.poll() is None
                for s in self._servers.values()
            )

    def stop(self, name: str) -> Dict:
        """Stop a running server by name."""
        with self._lock:
            if name not in self._servers:
                return {"name": name, "status": "not_found",
                        "error": f"No server named '{name}'"}
            return self._stop_one(name)

    def _stop_one(self, name: str) -> Dict:
        """Internal stop — caller must hold the lock (or be single-threaded)."""
        server = self._servers.pop(name, None)
        if not server:
            return {"name": name, "status": "not_found"}

        try:
            proc = server.process
            if proc.poll() is None:
                if IS_WINDOWS:
                    # Kill the whole process tree (shell=True spawns children).
                    subprocess.run(
                        f"taskkill /F /T /PID {proc.pid}",
                        shell=True, capture_output=True, timeout=10,
                    )
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                else:
                    import signal
                    proc.send_signal(signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            return {"name": name, "status": "stopped", "pid": server.pid}
        except Exception as e:
            return {"name": name, "status": "error", "error": str(e)}

    def stop_all(self):
        """Stop all running servers. Registered at exit."""
        with self._lock:
            names = list(self._servers.keys())
            for name in names:
                self._stop_one(name)

    # ── Introspection ──────────────────────────────────────────────────
    def list_servers(self) -> List[Dict]:
        servers = []
        with self._lock:
            for name, server in self._servers.items():
                is_alive = server.process.poll() is None
                servers.append({
                    "name": name,
                    "pid": server.pid,
                    "port": server.port,
                    "url": server.url,
                    "command": server.command,
                    "cwd": server.cwd,
                    "status": "running" if is_alive else "stopped",
                })
        return servers

    def running_names(self) -> List[str]:
        return [s["name"] for s in self.list_servers() if s["status"] == "running"]

    def is_running(self, name: str) -> bool:
        with self._lock:
            server = self._servers.get(name)
            return bool(server) and server.process.poll() is None

    def get_url(self, name: str) -> Optional[str]:
        with self._lock:
            server = self._servers.get(name)
            return server.url if server else None

    def get_output(self, name: str, last: int = 20) -> List[str]:
        """Last captured stdout/stderr lines for a server (for crash diagnostics)."""
        with self._lock:
            server = self._servers.get(name)
            return list(server._output_lines[-last:]) if server else []

    def open_in_browser(self, name: str = None) -> bool:
        """Open a server's URL in the default browser. No-op inside a container
        (no browser/display) — the UI prints a clickable URL instead."""
        if os.path.exists("/.dockerenv"):
            return False
        with self._lock:
            if name:
                server = self._servers.get(name)
            else:
                server = next(
                    (s for s in self._servers.values()
                     if s.process.poll() is None and s.url),
                    None,
                )
        if not server or not server.url:
            return False
        try:
            webbrowser.open(server.url)
            return True
        except Exception:
            return False

    # ── Output reader (port detection) ─────────────────────────────────
    def _read_output(self, server: ServerProcess):
        try:
            for line in iter(server.process.stdout.readline, ""):
                if not line:
                    break
                line = line.rstrip()
                server._output_lines.append(line)
                if len(server._output_lines) > 100:
                    server._output_lines = server._output_lines[-50:]

                if server.port is None:
                    for pattern in PORT_PATTERNS:
                        m = pattern.search(line)
                        if m:
                            server.port = int(m.group(1))
                            server.url = f"http://localhost:{server.port}"
                            server._port_event.set()
                            break
        except (ValueError, OSError):
            pass  # process closed stdout
        finally:
            server._port_event.set()  # unblock waiter even if no port found
