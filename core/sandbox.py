import os
import tempfile
import subprocess
from pathlib import Path
import re
import platform
import shutil


def force_host_binding(content: str, port: int = 5000) -> str:
    """Rewrite a web server's bind so it listens on 0.0.0.0:<port>.

    Used by the sandbox (always port 5000) and by /server, which assigns each
    app its own free port — generated apps hardcode 0.0.0.0:5000, so the port
    rewrite is what lets two or three apps run side by side without collisions.
    """
    # Flask: app.run(...) → app.run(host="0.0.0.0", port=<port>)
    if "Flask" in content and re.search(r"\.run\(", content):
        content = re.sub(
            r"\.run\([^)]*\)",
            f'.run(host="0.0.0.0", port={port})',
            content,
            count=1,
        )

    # FastAPI: uvicorn.run(app, ...) → uvicorn.run(app, host="0.0.0.0", port=<port>)
    m = re.search(r"uvicorn\.run\(\s*([^,)]+)", content)
    if m:
        first_arg = m.group(1).strip()
        content = re.sub(
            r"uvicorn\.run\([^)]*\)",
            f'uvicorn.run({first_arg}, host="0.0.0.0", port={port})',
            content,
            count=1,
        )

    # Express/Node: .listen(5000[, "host"]) → .listen(<port>, "0.0.0.0")
    content = re.sub(
        r"\.listen\(\s*\d+\s*(?:,\s*['\"][^'\"]*['\"])?",
        f'.listen({port}, "0.0.0.0"',
        content,
        count=1,
    )

    return content


class Sandbox:
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="darecode_"))

    def _strip_browser_commands(self, content: str) -> str:
        """Removes code trying to open browsers directly."""
        import_pattern = r"(import\s+webbrowser)|(from\s+webbrowser\s+import\s+.*)"
        call_pattern = r"(webbrowser\.open\([^)]*\))|(webbrowser\.open_new\([^)]*\))|(webbrowser\.open_new_tab\([^)]*\))"
        content = re.sub(import_pattern, "", content)
        content = re.sub(call_pattern, "pass  # Suppressed webbrowser call", content)
        return content

    def _force_host_binding(self, content: str) -> str:
        return force_host_binding(content, port=5000)

    def write_files(self, files: dict) -> None:
        """Writes ALL files to the workspace."""
        for filepath, content in files.items():
            path = self.workspace_dir / filepath
            path.parent.mkdir(parents=True, exist_ok=True)
            clean_content = self._force_host_binding(self._strip_browser_commands(content))
            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_content)
                
            temp_path = self.temp_dir / filepath
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(clean_content)

    def is_web_server(self, files: dict, entrypoint: str = None) -> bool:
        """Detect if the code starts a local web server.
        
        If entrypoint is provided, only checks files in the same project
        directory as the entrypoint (not the entire workspace).
        """
        if entrypoint:
            project_dir = str(Path(entrypoint).parent)
            if project_dir == ".":
                # Entrypoint is at workspace root — only check root-level files
                check_files = {k: v for k, v in files.items() if "/" not in k and "\\" not in k}
            else:
                # Only check files in the same project directory
                check_files = {k: v for k, v in files.items() if k.startswith(project_dir + "/")}
        else:
            check_files = files

        for content in check_files.values():
            if "app.run(" in content and "Flask" in content:
                return True
            if "uvicorn.run(" in content and "FastAPI" in content:
                return True
            if "http.server" in content or "SimpleHTTPServer" in content:
                return True
            if "express()" in content and ".listen(" in content:
                return True
        return False

    def _open_browser(self, url: str):
        """Platform-aware browser opening logic.

        Inside a container there is no browser/display, so we skip silently and
        rely on the URL printed by the /execute handler for manual open.
        """
        if os.path.exists("/.dockerenv"):
            return
        if platform.system() == "Windows":
            subprocess.Popen(["cmd.exe", "/c", f"start {url}"], shell=False)
        else:
            if shutil.which("wslview"):
                subprocess.Popen(["wslview", url])
            elif shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", url])

    def execute(self, files: dict, entrypoint: str = "main.py", timeout: int = 30, stdin_data: str = None) -> dict:
        """Executes code via Docker sandbox, falling back to local Python if missing.
        
        Args:
            stdin_data: Optional string to pipe as stdin to the process.
                        If None, stdin is closed (DEVNULL) to prevent hangs on input().
        """
        self.write_files(files)
        
        # Resolve the entrypoint
        abs_entrypoint = self.temp_dir / entrypoint
        if not abs_entrypoint.exists() or not abs_entrypoint.is_file():
            return {"exit_code": 1, "stdout": "", "stderr": f"Entrypoint '{entrypoint}' is not a valid file."}
            
        ext = abs_entrypoint.suffix
        if ext == ".py":
            cmd = ["python", entrypoint]
            image = "python:3.10-slim"
        elif ext == ".js":
            cmd = ["node", entrypoint]
            image = "node:18-slim"
        elif ext == ".sh":
            cmd = ["bash", entrypoint]
            image = "ubuntu:22.04"
        else:
            cmd = [entrypoint]
            image = "ubuntu:22.04"

        try:
            # Check for Docker
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{self.temp_dir.absolute()}:/app",
                "-w", "/app",
                "--network", "host" if self.is_web_server(files, entrypoint) else "none",
                image
            ] + cmd

            if self.is_web_server(files, entrypoint):
                # Web server logic
                process = subprocess.Popen(
                    docker_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                import time
                time.sleep(2)  # Wait for server to bind
                if process.poll() is None:
                    # Still running, assume success
                    self._open_browser("http://localhost:5000")
                    return {"exit_code": 0, "stdout": "Web server running.", "stderr": ""}
                
                # Server crashed
                out, err = process.communicate()
                return {"exit_code": process.returncode, "stdout": out, "stderr": err}
            else:
                # Normal script execution
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=timeout,
                    input=stdin_data,
                    stdin=subprocess.DEVNULL if stdin_data is None else None
                )
                return {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Docker not available or failed, fallback to local execution
            if self.is_web_server(files, entrypoint):
                process = subprocess.Popen(
                    cmd,
                    cwd=str(self.temp_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                import time
                time.sleep(2)
                if process.poll() is None:
                    self._open_browser("http://localhost:5000")
                    return {"exit_code": 0, "stdout": "Web server running locally.", "stderr": ""}
                out, err = process.communicate()
                return {"exit_code": process.returncode, "stdout": out, "stderr": err}
            else:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=str(self.temp_dir),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=timeout,
                        input=stdin_data,
                        stdin=subprocess.DEVNULL if stdin_data is None else None
                    )
                    return {
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                except subprocess.TimeoutExpired:
                    return {"exit_code": 1, "stdout": "", "stderr": f"Execution timed out after {timeout} seconds"}

    def cleanup(self):
        """Removes the temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
