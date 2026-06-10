"""
Slash-command handlers for DareCode (ported/adapted from the old ui.py).

These are plain functions that take the live `console` and `agent` so `main.py`
stays a thin dispatcher. They run synchronously outside the pipeline Live display,
so prompting with input()/Prompt is safe here.
"""

import os
import json
from pathlib import Path

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt

from ui.ascii_art import DAREDEVIL_MASK
from core.harnesses import harness, summarize_run

SNIPPETS_DIR = Path(__file__).resolve().parent.parent / "snippets"

KNOWN_MODELS = {
    "opus": "eu.anthropic.claude-opus-4-6-v1",
    "qwen": "qwen.qwen3-235b-a22b-2507-v1:0",
}


# ── Header (shared by startup + /clear) ──────────────────────────────────────
def print_header(console):
    console.print(Panel(
        Text.from_markup(
            DAREDEVIL_MASK + "\n\n"
            f"[bold red]  DareCode[/bold red]  [red]v2.0[/red]\n"
            f"[italic]  The Man Without Fear... of Bugs[/italic]\n\n"
            f"[red]  ● Code Generation  ● Execution  ● Self-Debug[/red]\n"
            f"[red]  ● Defenders Mode[/red]\n\n"
            f"[dim]  Type / to see all commands[/dim]"
        ),
        border_style="bold red",
        padding=(1, 2)
    ))


# ── /clear ───────────────────────────────────────────────────────────────────
def cmd_clear(console):
    console.clear()
    print_header(console)


# ── /history ─────────────────────────────────────────────────────────────────
def _block_preview(blocks) -> str:
    """Turn a Bedrock content-block list into a short human label."""
    texts = []
    for b in blocks:
        if "text" in b:
            texts.append(b["text"].strip().replace("\n", " "))
        elif "toolUse" in b:
            texts.append(f"→ called {b['toolUse'].get('name', '?')}")
        elif "toolResult" in b:
            status = b["toolResult"].get("status", "?")
            texts.append(f"(tool result: {status})")
    joined = " ".join(t for t in texts if t)
    return joined[:140] + ("…" if len(joined) > 140 else "")


def cmd_history(console, agent):
    if not agent.history:
        console.print("[dim]No conversation history yet.[/dim]")
        return
    from rich.rule import Rule
    console.print(Rule("[bold red]Conversation History[/bold red]", style="red"))
    for i, msg in enumerate(agent.history, 1):
        role = msg.get("role", "?")
        preview = _block_preview(msg.get("content", []))
        if not preview:
            continue
        who = "[red]You[/red]" if role == "user" and not preview.startswith("(tool result") else \
              ("[dim white]Tool[/dim white]" if preview.startswith("(tool result") else "[bold]DareCode[/bold]")
        console.print(f"  [bold red]{i}.[/bold red] {who}: {preview}")
    console.print()


# ── /stats ───────────────────────────────────────────────────────────────────
def _snippet_count() -> int:
    if not SNIPPETS_DIR.exists():
        return 0
    return sum(1 for _ in SNIPPETS_DIR.glob("*.json"))


def cmd_stats(console, agent):
    m = agent.metrics
    table = Table(title="[bold red]Session Statistics[/bold red]", border_style="red")
    table.add_column("Metric", style="bold red")
    table.add_column("Value", style="bold white")

    table.add_row("Messages", str(len(agent.history)))
    table.add_row("Requests", str(m["requests"]))
    table.add_row("LLM Calls", str(m["llm_calls"]))
    table.add_row("Tool Calls", str(m["tool_calls"]))
    table.add_row("Tool Successes", f"[green]{m['tool_successes']}[/green]")
    table.add_row("Tool Failures", f"[red]{m['tool_failures']}[/red]" if m["tool_failures"] else "0")
    table.add_row("Files Written", str(m["files_written"]))
    table.add_row("Saved Snippets", str(_snippet_count()))
    table.add_row("Model", agent.brain.model_id)
    table.add_row("Region", agent.brain.region)
    table.add_row("Harness", "[green]on[/green]" if harness.enabled else "[dim]off[/dim]")
    if agent.current_project:
        table.add_row("Active Project", agent.current_project)
    console.print(table)


# ── /test ────────────────────────────────────────────────────────────────────
def cmd_test(console, agent):
    files = dict(agent.last_run_files)
    if not files:
        console.print("[dim]No recent code to test. Generate some code first.[/dim]")
        return

    combined = "\n\n".join(f"# File: {p}\n{c}" for p, c in files.items())
    console.print("[dim]Generating tests…[/dim]")
    prompt = (
        "Generate comprehensive, runnable test cases for the following code. "
        "Use plain asserts or the unittest module so it runs with `python <file>` "
        "(no pytest). Cover edge cases. Reply with ONE code block only.\n\n"
        f"{combined}"
    )
    response = agent.brain.think(
        [{"role": "user", "content": [{"text": prompt}]}],
        system="You are a meticulous test engineer. Output a single runnable test file."
    )

    test_code = _extract_code_block(response)
    if not test_code:
        console.print(Panel(response, border_style="red", title="[bold red]Test Cases[/bold red]"))
        return

    console.print(Syntax(test_code, "python", theme="monokai", line_numbers=True))

    try:
        run = Prompt.ask("[bold red]Run these tests? [y/n][/bold red]", default="n").strip().lower()
    except (EOFError, KeyboardInterrupt):
        run = "n"
    if run != "y":
        return

    # Run the tests alongside the code under test, in a sandbox.
    from core.sandbox import Sandbox
    base = _common_dir(files.keys())
    sandbox_files = {os.path.relpath(p, base).replace("\\", "/"): c for p, c in files.items()}
    sandbox_files["test_generated.py"] = test_code

    console.print("[dim]Running tests in sandbox…[/dim]")
    result = Sandbox().execute(sandbox_files, "test_generated.py")
    if result.get("exit_code", 1) == 0:
        console.print(Panel(result.get("stdout") or "Tests passed (no output).",
                            border_style="green", title="[bold green]Test Output[/bold green]"))
    else:
        console.print(Panel(result.get("stderr") or result.get("stdout") or "Tests failed.",
                            border_style="red", title="[bold red]Test Failure[/bold red]"))


def _extract_code_block(text: str) -> str:
    import re
    m = re.search(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL)
    return m.group(1).strip() if m else ""


def _common_dir(paths) -> str:
    dirs = [os.path.dirname(p) or "." for p in paths]
    try:
        return os.path.commonpath(dirs) if len(dirs) > 1 else dirs[0]
    except ValueError:
        return "."


# ── /snippet ─────────────────────────────────────────────────────────────────
def cmd_snippet(console, agent, args):
    name = args.strip()
    if not name:
        # List saved snippets
        if not SNIPPETS_DIR.exists() or not any(SNIPPETS_DIR.glob("*.json")):
            console.print("[dim]No saved snippets. Use /snippet <name> after writing code.[/dim]")
            return
        console.print("[bold red]Saved snippets:[/bold red]")
        for f in sorted(SNIPPETS_DIR.glob("*.json")):
            console.print(f"  [red]•[/red] {f.stem}")
        return

    if not agent.last_run_files:
        console.print("[dim]No recent code to save. Generate some code first.[/dim]")
        return

    SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in name if c.isalnum() or c in ("_", "-")) or "snippet"
    path = SNIPPETS_DIR / f"{safe}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"name": safe, "files": agent.last_run_files}, f, indent=2)
    console.print(f"[green]✓ Snippet '{safe}' saved ({len(agent.last_run_files)} file(s)).[/green]")


# ── /model ───────────────────────────────────────────────────────────────────
def cmd_model(console, agent, args):
    target = args.strip()
    if not target:
        console.print(f"[bold red]Current model:[/bold red] {agent.brain.model_id}")
        console.print("[dim]Known aliases:[/dim]")
        for alias, mid in KNOWN_MODELS.items():
            console.print(f"  [red]{alias}[/red] → {mid}")
        console.print("[dim]Usage: /model <alias|full-model-id>[/dim]")
        return

    model_id = KNOWN_MODELS.get(target.lower(), target)
    agent.brain.reconfigure(model_id=model_id)
    console.print(f"[green]✓ Model switched to {model_id}. No restart needed.[/green]")
    return model_id  # main.py persists this in Phase 2


# ── /change api ──────────────────────────────────────────────────────────────
def cmd_change_api(console, agent):
    console.print("[dim]Update Bedrock credentials (blank = keep current).[/dim]")
    try:
        new_key = Prompt.ask("[bold red]New API key (Bearer token)[/bold red]", default="").strip()
        region = Prompt.ask("[bold red]Region[/bold red]", default=agent.brain.region).strip()
        model = Prompt.ask("[bold red]Model ID[/bold red]", default=agent.brain.model_id).strip()
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow]Cancelled.[/yellow]")
        return None

    agent.brain.reconfigure(
        model_id=model or None,
        region=region or None,
        api_key=new_key or None,
    )
    console.print("[green]✓ Credentials updated. No restart needed.[/green]")
    return {"region": agent.brain.region, "model": agent.brain.model_id, "key_changed": bool(new_key)}


# ── /harness ─────────────────────────────────────────────────────────────────
def cmd_harness(console, args):
    action = args.strip().lower()

    if action == "on":
        harness.set_enabled(True)
        console.print("[red]Harness enabled.[/red]")
    elif action == "off":
        harness.set_enabled(False)
        console.print("[red]Harness disabled.[/red]")
    elif action == "show":
        run = harness.last_run()
        if not run:
            console.print("[dim]No harness run in memory yet.[/dim]")
            return
        table = Table(title=f"[bold red]Harness · Run {run.id}[/bold red]", border_style="red")
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Category", style="bold")
        table.add_column("Name", style="white")
        table.add_column("Status", justify="center")
        table.add_column("ms", justify="right", style="cyan")
        for evt in run.events:
            color = {"ok": "green", "error": "red"}.get(evt.status, "yellow")
            dur = f"{evt.duration_ms:.0f}" if evt.duration_ms is not None else "—"
            table.add_row(str(evt.id), evt.category, evt.name,
                          f"[{color}]{evt.status}[/{color}]", dur)
        console.print(table)
        saved = harness.save_run(run)
        if saved:
            console.print(f"[dim]Saved to: {saved[0]}[/dim]")
    elif action in ("summary on", "summary"):
        harness.summary = True
        console.print("[red]Post-run harness summary enabled.[/red]")
    elif action == "summary off":
        harness.summary = False
        console.print("[red]Post-run harness summary disabled.[/red]")
    else:
        console.print("[dim]Usage: /harness on | off | show | summary on|off[/dim]")
        console.print(f"[dim]Currently: {'on' if harness.enabled else 'off'}, "
                      f"summary {'on' if harness.summary else 'off'}.[/dim]")


def _fmt_ms(ms):
    if ms is None:
        return "—"
    if ms < 1000:
        return f"{int(round(ms))} ms"
    return f"{ms / 1000:.2f}s"


def print_harness_summary(console, run):
    """Detailed post-run timeline panel (the full event table is /harness show)."""
    if run is None or not harness.summary:
        return
    s = summarize_run(run)
    if s.get("status") == "empty":
        return

    has_error = bool(s["errors"]) or s["status"] == "error"
    border = "red" if has_error else "green"
    wall = _fmt_ms(s.get("duration_ms"))
    title_status = "[red]error[/red]" if has_error else "[green]ok[/green]"

    table = Table(
        title=f"[bold]Harness · Run {run.id} · {title_status} · {wall}[/bold]",
        border_style=border, title_justify="center", expand=False, padding=(0, 1),
    )
    table.add_column("#", style="dim", justify="right")
    table.add_column("Step", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right", style="cyan")
    table.add_column("Tokens", justify="right", style="magenta")

    timeline = s.get("timeline") or []
    MAX_ROWS = 15
    for i, step in enumerate(timeline[:MAX_ROWS], start=1):
        st = step.get("status", "ok")
        st_txt = "[green]ok[/green]" if st == "ok" else "[red]error[/red]"
        tok = step.get("tokens")
        tok_txt = f"{tok:,}" if isinstance(tok, (int, float)) else "—"
        table.add_row(str(i), step.get("label", "?"), st_txt,
                      _fmt_ms(step.get("duration_ms")), tok_txt)
    if len(timeline) > MAX_ROWS:
        table.add_row("", f"[dim]… {len(timeline) - MAX_ROWS} more steps[/dim]", "", "", "")

    tokens = s.get("total_tokens") or 0
    tok_str = f"{tokens:,}" if tokens else "—"
    table.caption = (f"Total: {wall} · {s['llm_calls']} LLM call(s) · "
                     f"{s['tool_calls']} tool call(s) · {tok_str} tokens · {len(s['errors'])} error(s)")
    table.caption_style = "red" if has_error else "dim"

    console.print(table)
    for err in s["errors"][:3]:
        console.print(f"[red]⚠ {err}[/red]")
