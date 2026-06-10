import subprocess
import platform
import shutil
import inspect
import glob as glob_module
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

_console = Console()

_active_display = None

def set_display(display):
    global _active_display
    _active_display = display

def _get_shell_cmd(command: str) -> list:
    """Pick the right shell based on where we're running."""
    # Inside WSL/Linux/Docker → bash is native
    if platform.system() != "Windows":
        return ["bash", "-c", command]
    # On Windows PowerShell → forward to WSL
    if shutil.which("wsl.exe"):
        return ["wsl.exe", "bash", "-c", command]
    # Fallback Windows (git bash, etc.)
    return ["cmd.exe", "/c", command]

def _ask_permission(action_text: str) -> bool:
    """Prompt the user for permission before doing something dangerous."""
    if _active_display:
        _active_display.pause()
        
    print("\n")  # breathing room before permission
    _console.print(Panel(
        f"[bold white]{action_text}[/bold white]",
        title="[bold yellow]⚡ Permission Required[/bold yellow]",
        border_style="yellow",
        padding=(0, 2),
        width=60
    ))
    
    try:
        choice = input("  Allow? [y/n] → ").strip().lower()
        print()  # breathing room after
    except (EOFError, KeyboardInterrupt):
        choice = "n"
        print()
        
    if _active_display:
        _active_display.resume()
    
    if choice != "y":
        _console.print("  [dim red]✗ Denied[/dim red]")
        return False
    
    _console.print("  [dim green]✓ Approved[/dim green]")
    return True

# ── 1. BASH ──────────────────────────────────────────────────────────────────
SAFE_COMMANDS = ["ls", "cat", "echo", "pwd", "find", "grep", "head", "tail", "wc", "tree", "cd", "which", "whoami", "date", "uname"]

def bash(command: str, timeout: int = 30) -> dict:
    """Run a shell command. Returns stdout, stderr, exit code."""
    cmd_base = command.strip().split()[0] if command.strip() else ""
    
    if cmd_base not in SAFE_COMMANDS:
        if not _ask_permission(command):
            return {"stdout": "", "stderr": "User denied.", "exit_code": 1}
            
    try:
        result = subprocess.run(
            _get_shell_cmd(command),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out.", "exit_code": 1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1}


# ── 2. GLOB ───────────────────────────────────────────────────────────────────
def glob(pattern: str, base_dir: str = ".") -> dict:
    """Find files matching a pattern. Example: '**/*.py'"""
    try:
        base = Path(base_dir).resolve()
        matches = list(base.glob(pattern))
        files = [str(m.relative_to(base)) for m in matches if m.is_file()]
        return {
            "matches": files,
            "count": len(files)
        }
    except Exception as e:
        return {"matches": [], "count": 0, "error": str(e)}


# ── 3. FILE_READ ──────────────────────────────────────────────────────────────
def file_read(path: str) -> dict:
    """Read the full content of a file."""
    try:
        content = Path(path).read_text(encoding="utf-8")
        lines = content.splitlines()
        return {
            "content": content,
            "lines": len(lines),
            "path": path
        }
    except FileNotFoundError:
        return {"content": "", "error": f"File not found: {path}"}
    except Exception as e:
        return {"content": "", "error": str(e)}


# ── 4. GREP ───────────────────────────────────────────────────────────────────
def grep(pattern: str, path: str, case_sensitive: bool = True) -> dict:
    """Search for a pattern inside a file. Returns matching lines."""
    try:
        content = Path(path).read_text(encoding="utf-8")
        lines = content.splitlines()

        if not case_sensitive:
            matches = [
                {"line": i + 1, "content": line}
                for i, line in enumerate(lines)
                if pattern.lower() in line.lower()
            ]
        else:
            matches = [
                {"line": i + 1, "content": line}
                for i, line in enumerate(lines)
                if pattern in line
            ]

        return {
            "matches": matches,
            "count": len(matches),
            "pattern": pattern,
            "path": path
        }
    except FileNotFoundError:
        return {"matches": [], "error": f"File not found: {path}"}
    except Exception as e:
        return {"matches": [], "error": str(e)}


# ── 5. WRITE_FILE ─────────────────────────────────────────────────────────────
def write_file(path: str, content: str) -> dict:
    """Write content to a file. Creates parent directories if needed."""
    try:
        target = Path(path)
        
        # LEVEL 2 WORKSPACE ENFORCEMENT
        if "workspace" not in target.resolve().parts and "workspace" not in target.parts:
            if not _ask_permission(f"WRITE OUTSIDE WORKSPACE:\n{path}"):
                return {"success": False, "error": "User denied file write outside workspace."}
                
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "path": str(target.resolve()),
            "bytes_written": len(content.encode("utf-8"))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── 6. FILE_EDIT ─────────────────────────────────────────────────────────────
def file_edit(path: str, old_text: str, new_text: str) -> dict:
    """Surgically replace old_text with new_text in a file."""
    try:
        target = Path(path)
        
        # LEVEL 2 WORKSPACE ENFORCEMENT
        if "workspace" not in target.resolve().parts and "workspace" not in target.parts:
            if not _ask_permission(f"EDIT OUTSIDE WORKSPACE:\n{path}"):
                return {"success": False, "error": "User denied file edit outside workspace."}
                
        content = target.read_text(encoding="utf-8")
        count = content.count(old_text)
        if count == 0:
            return {"success": False, "error": f"old_text not found in {path}"}
        if count > 1:
            return {"success": False, "error": f"old_text found {count} times in {path}. Must be exactly 1 to avoid ambiguity."}
        
        new_content = content.replace(old_text, new_text)
        Path(path).write_text(new_content, encoding="utf-8")
        return {
            "success": True,
            "path": path,
            "replacements": 1
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── TOOL REGISTRY ─────────────────────────────────────────────────────────────
TOOLS = {
    "bash":       bash,
    "glob":       glob,
    "file_read":  file_read,
    "grep":       grep,
    "write_file": write_file,
    "file_edit":  file_edit,
}

def run_tool(name: str, **kwargs) -> dict:
    """Dispatch a tool call by name."""
    if name not in TOOLS:
        return {"error": f"Unknown tool: {name}"}

    # Strip kwargs the LLM hallucinated
    func = TOOLS[name]
    valid = set(inspect.signature(func).parameters.keys())
    clean = {k: v for k, v in kwargs.items() if k in valid}

    return func(**clean)


# ── BEDROCK TOOL SPECS ────────────────────────────────────────────────────────
# Native tool-use schemas for the Converse API (toolConfig.tools). These mirror
# the TOOLS registry above so the model emits structured `toolUse` blocks instead
# of fragile free-text JSON.
TOOL_SPECS = [
    {
        "toolSpec": {
            "name": "bash",
            "description": "Run a shell command and return its stdout, stderr, and exit_code. "
                           "Use this to run code, list files, or inspect the environment.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The shell command to execute."},
                        "timeout": {"type": "integer", "description": "Max seconds to wait (default 30)."},
                    },
                    "required": ["command"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "glob",
            "description": "Find files matching a glob pattern (e.g. '**/*.py'). Returns matching paths.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Glob pattern, e.g. '**/*.py'."},
                        "base_dir": {"type": "string", "description": "Directory to search from (default '.')."},
                    },
                    "required": ["pattern"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "file_read",
            "description": "Read the full UTF-8 content of a file. Always read a file before editing it.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to read."},
                    },
                    "required": ["path"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "grep",
            "description": "Search for a pattern inside a single file. Returns matching lines with line numbers.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Substring to search for."},
                        "path": {"type": "string", "description": "Path to the file to search."},
                        "case_sensitive": {"type": "boolean", "description": "Case-sensitive match (default true)."},
                    },
                    "required": ["pattern", "path"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content. Creates parent directories. "
                           "Keep all work inside the workspace/ directory.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to write, e.g. 'workspace/app.py'."},
                        "content": {"type": "string", "description": "Full file content to write."},
                    },
                    "required": ["path", "content"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "file_edit",
            "description": "Surgically replace old_text with new_text in a file. old_text must appear "
                           "exactly once. Read the file first to get exact text.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to edit."},
                        "old_text": {"type": "string", "description": "Exact text to replace (must be unique)."},
                        "new_text": {"type": "string", "description": "Replacement text."},
                    },
                    "required": ["path", "old_text", "new_text"],
                }
            },
        }
    },
]
