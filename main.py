import sys
import json
import re
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from core.agent import Agent
from ui.theme import PipelineDisplay
from ui.mascot import print_spider
from ui.commands import get_prompt_session
from ui.personas import DAREDEVIL, MATT_MURDOCK
from ui.animations import AnimationEngine
from memory.session import SessionManager
from ui.ascii_art import DAREDEVIL_MASK
from ui import command_handlers as ch
from core import harnesses
from core.harnesses import harness
from core.settings import Settings, apply_settings
from core.server_manager import ServerManager
from core.project_manager import ProjectManager
from pathlib import Path

def print_response(console, text, color="red"):
    """Print response with syntax-highlighted code blocks."""
    parts = re.split(r'(```\w*\n.*?```)', text, flags=re.DOTALL)
    
    for part in parts:
        match = re.match(r'```(\w*)\n(.*?)```', part, flags=re.DOTALL)
        if match:
            lang = match.group(1) or "python"
            code = match.group(2)
            console.print(Syntax(code.strip(), lang, theme="monokai", line_numbers=True))
        else:
            if part.strip():
                console.print(part.strip())

def main():
    agent = Agent()
    console = Console()
    current_persona = DAREDEVIL
    current_color = "#CC0000"

    # Persistent settings (~/.darecode/config.json) — model/region/harness/team
    # survive restarts. The API key stays in .env and is never persisted here.
    settings = Settings()
    apply_settings(agent.brain, settings)
    harnesses.init(
        enabled=settings.get("harness_enabled", True),
        summary=settings.get("harness_summary", True),
    )

    server_manager = ServerManager()
    project_manager = ProjectManager(Path("workspace"))

    ch.print_header(console)

    session = get_prompt_session(current_color)
    display = PipelineDisplay(console, current_color)
    anim_engine = AnimationEngine(console, current_persona)
    session_manager = SessionManager(agent)

    while True:
        print_spider("IDLE", current_color)
        try:
            user_input = session.prompt([('class:prompt', f'{current_persona.prompt_char} ')]).strip()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
            
        if not user_input:
            continue
            
        if user_input in ("/exit", "/quit"):
            if len(agent.history) > 2:
                console.print("[dim]Auto-saving session...[/dim]")
                session_manager.save()
            console.print("Shutting down.")
            break
            
        if user_input.startswith("/save"):
            console.print("[dim]Saving session...[/dim]")
            path = session_manager.save()
            if path:
                console.print(f"[green]Session saved to {path}[/green]")
            else:
                console.print("[yellow]Not enough conversation history to save.[/yellow]")
            continue
            
        if user_input.startswith("/sessions"):
            sessions = session_manager.get_sessions()
            if not sessions:
                console.print("[yellow]No saved sessions found.[/yellow]")
                continue
                
            console.print("\n  [bold white]Saved Sessions:[/bold white]")
            for i, s in enumerate(sessions, 1):
                title = s['title']
                padding = " " * max(1, 40 - len(title))
                console.print(f"  [cyan]{i}.[/cyan] {title}{padding}[dim]({s['date']})[/dim]")
                
            console.print("\n[dim]Type the number to load, or /back to cancel.[/dim]")
            
            try:
                choice = session.prompt([('class:prompt', '  > ')]).strip()
                if choice == '/back' or not choice:
                    continue
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    if session_manager.load(sessions[idx]['path']):
                        console.print(f"[green]Loaded session: {sessions[idx]['title']}[/green]")
                    else:
                        console.print("[red]Failed to load session.[/red]")
                else:
                    console.print("[red]Invalid selection.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Must be a number.[/red]")
            continue
            
        # ── Ported power-commands (Phase 1) ──────────────────────────────
        if user_input == "/clear":
            ch.cmd_clear(console)
            continue

        if user_input.startswith("/history"):
            ch.cmd_history(console, agent)
            continue

        if user_input.startswith("/stats"):
            ch.cmd_stats(console, agent)
            continue

        if user_input.startswith("/test"):
            ch.cmd_test(console, agent)
            continue

        if user_input.startswith("/snippet"):
            ch.cmd_snippet(console, agent, user_input[len("/snippet"):])
            continue

        # NOTE: must precede /mode — "/model".startswith("/mode") is True.
        if user_input.startswith("/model"):
            new_model = ch.cmd_model(console, agent, user_input[len("/model"):])
            if new_model:
                settings.set("model", new_model)
            continue

        if user_input.startswith("/change"):
            changed = ch.cmd_change_api(console, agent)
            if changed:
                settings.set("model", changed["model"], save=False)
                settings.set("region", changed["region"])
            continue

        if user_input.startswith("/harness"):
            ch.cmd_harness(console, user_input[len("/harness"):], settings)
            continue

        if user_input.startswith("/server"):
            ch.cmd_server(console, server_manager, project_manager,
                          user_input[len("/server"):])
            continue

        if user_input.startswith("/project"):
            ch.cmd_project(console, agent, project_manager,
                           user_input[len("/project"):])
            continue

        if user_input.startswith("/team"):
            ch.cmd_team(console, settings, user_input[len("/team"):])
            continue

        if user_input.startswith("/mode"):
            if current_persona == DAREDEVIL:
                current_persona = MATT_MURDOCK
                current_color = "#003366"
                console.print("[bold #003366]Switched to Matt Murdock (Blue) mode.[/bold #003366]")
            else:
                current_persona = DAREDEVIL
                current_color = "#CC0000"
                console.print("[bold #CC0000]Switched to Daredevil (Red) mode.[/bold #CC0000]")
            session = get_prompt_session(current_color)
            display.set_color(current_color)
            anim_engine.persona = current_persona
            continue
            
        if user_input.startswith("/explain"):
            prompt = user_input[len("/explain"):].strip()
            if not prompt: prompt = "What would you like explained?"
            display.start()
            display.update_stage("Classifying", "done", "Single-shot: Explain")
            display.update_stage("Routing", "skip")
            display.update_stage("Thinking", "running")
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            sys_prompt = "You are an expert explainer. Explain this code simply and clearly."
            res = agent.brain.think(messages, system=sys_prompt)
            display.update_stage("Thinking", "done")
            display.finish()
            print_spider("SUCCESS", current_color)
            print()
            print_response(console, res, current_color)
            print()
            continue
            
        if user_input.startswith("/review"):
            prompt = user_input[len("/review"):].strip()
            if not prompt: prompt = "Review the current project structure and codebase."
            display.start()
            display.update_stage("Classifying", "done", "Single-shot: Review")
            display.update_stage("Routing", "skip")
            display.update_stage("Thinking", "running")
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            sys_prompt = "You are an expert reviewer. Review this code for correctness and performance."
            res = agent.brain.think(messages, system=sys_prompt)
            display.update_stage("Thinking", "done")
            display.finish()
            print_spider("SUCCESS", current_color)
            print()
            print_response(console, res, current_color)
            print()
            continue
            
        if user_input.startswith("/plan"):
            prompt = user_input[len("/plan"):].strip()
            if not prompt: prompt = "What would you like to plan?"
            display.start()
            display.update_stage("Classifying", "done", "Single-shot: Plan")
            display.update_stage("Routing", "skip")
            display.update_stage("Thinking", "running")
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            sys_prompt = "You are a master architect. Write a detailed implementation plan."
            res = agent.brain.think(messages, system=sys_prompt)
            display.update_stage("Thinking", "done")
            display.finish()
            print_spider("SUCCESS", current_color)
            print()
            print_response(console, res, current_color)
            print()
            continue
            
        if user_input.startswith("/coffee"):
            prompt = user_input[len("/coffee"):].strip()
            if not prompt: prompt = "Let's just chat for a bit."
            anim_engine.play_coffee_break()
            display.start()
            display.update_stage("Classifying", "done", "Coffee Break")
            display.update_stage("Routing", "skip")
            display.update_stage("Thinking", "running")
            messages = [{"role": "user", "content": [{"text": prompt}]}]
            sys_prompt = "You are DareCode. We are taking a coffee break at Josie's Bar. Just chat casually."
            res = agent.brain.think(messages, system=sys_prompt)
            display.update_stage("Thinking", "done")
            display.finish()
            print()
            print_response(console, res, current_color)
            print()
            continue

        active_anim_engine = anim_engine if current_persona.mode == "dark" else None

        # /team on: route plain requests through the Defenders flow below.
        if settings.get("defenders_auto", False) and not user_input.startswith("/"):
            console.print("[dim]Team auto-mode: assembling the Defenders…[/dim]")
            user_input = "/defenders " + user_input

        if user_input.startswith("/defenders"):
            prompt = user_input[len("/defenders"):].strip()
            if not prompt: prompt = "What task do you want the Defenders to tackle?"
            
            if active_anim_engine:
                active_anim_engine.play_team_assembly(["daredevil", "jessica_jones", "luke_cage", "iron_fist", "spider_man"])
                
            display.start()
            display.update_stage("Classifying", "done", "Defenders Assembly")
            display.update_stage("Routing", "done", "Team Orchestration")
            display.update_stage("Thinking", "running")
            
            system_prompt = """Break this task into 2-4 subtasks. Assign each to the right Defender.
Respond ONLY with a JSON array, nothing else:
[{"defender": "luke", "task": "..."}, {"defender": "spider", "task": "..."}, {"defender": "iron", "task": "review all generated code"}]

Available defenders:
- jessica: debugging, error investigation
- luke: backend, APIs, databases, algorithms
- spider: frontend, HTML, CSS, JS, React
- iron: code review (always runs last)"""

            messages = [{"role": "user", "content": [{"text": prompt}]}]
            res = agent.brain.think(messages, system=system_prompt)
            display.update_stage("Thinking", "done")
            
            try:
                subtasks = json.loads(res.strip())
            except json.JSONDecodeError:
                subtasks = [
                    {"defender": "luke", "task": f"Build backend for: {prompt}"},
                    {"defender": "spider", "task": f"Build frontend for: {prompt}"},
                    {"defender": "iron", "task": "Review all generated code"}
                ]
                
            from skills.jessica import JessicaJones
            from skills.luke import LukeCage
            from skills.spiderman import SpiderMan
            
            final_result = ""
            for st in subtasks:
                defender = st.get("defender")
                subtask_prompt = st.get("task")
                
                print_spider("THINKING", current_color)
                if defender == "jessica":
                    if active_anim_engine: active_anim_engine.play_hero_intro("jessica_jones")
                    res = agent.run(subtask_prompt, display, animation=active_anim_engine, active_system_prompt=JessicaJones.SYSTEM_PROMPT)
                elif defender == "luke":
                    if active_anim_engine: active_anim_engine.play_hero_intro("luke_cage")
                    res = agent.run(subtask_prompt, display, animation=active_anim_engine, active_system_prompt=LukeCage.SYSTEM_PROMPT)
                elif defender == "spider":
                    if active_anim_engine: active_anim_engine.play_hero_intro("spider_man")
                    res = agent.run(subtask_prompt, display, animation=active_anim_engine, active_system_prompt=SpiderMan.SYSTEM_PROMPT)
                elif defender == "iron":
                    display.update_stage("Classifying", "done", "Skipped (Unified)")
                    display.update_stage("Routing", "done", "Iron Fist")
                    display.update_stage("Thinking", "running")
                    if active_anim_engine: active_anim_engine.play_hero_intro("iron_fist")
                    res = agent.ironfist.review(final_result or "No code generated yet.")
                    display.update_stage("Thinking", "done")
                else:
                    res = agent.run(subtask_prompt, display, animation=active_anim_engine)
                    
                final_result += f"\n\n--- {defender.upper() if defender else 'DARECODE'} ---\n{res}"
                
            display.finish()
            if active_anim_engine and "Iron Fist Review" in final_result:
                active_anim_engine.play_victory()
                
            print()
            print_response(console, final_result, current_color)
            print()
            continue

        if user_input.startswith("/jessica"):
            prompt = user_input[len("/jessica"):].strip()
            if not prompt: prompt = "What do you want Jessica to debug?"
            if active_anim_engine: active_anim_engine.play_hero_intro("jessica_jones")
            from skills.jessica import JessicaJones
            display.start()
            try:
                result = agent.run(prompt, display, animation=active_anim_engine, active_system_prompt=JessicaJones.SYSTEM_PROMPT)
                display.finish()
                print_spider("SUCCESS", current_color)
                if active_anim_engine and result and "Iron Fist Review" in result: active_anim_engine.play_victory()
                if result:
                    print()
                    print_response(console, result, current_color)
                    print()
            except Exception as e:
                display.update_stage("Thinking", "error")
                display.finish()
                if active_anim_engine: active_anim_engine.play_spider_error(str(e))
                else: print_spider("ERROR", current_color)
            continue

        if user_input.startswith("/luke"):
            prompt = user_input[len("/luke"):].strip()
            if not prompt: prompt = "What backend task do you want Luke to handle?"
            if active_anim_engine: active_anim_engine.play_hero_intro("luke_cage")
            from skills.luke import LukeCage
            display.start()
            try:
                result = agent.run(prompt, display, animation=active_anim_engine, active_system_prompt=LukeCage.SYSTEM_PROMPT)
                display.finish()
                print_spider("SUCCESS", current_color)
                if active_anim_engine and result and "Iron Fist Review" in result: active_anim_engine.play_victory()
                if result:
                    print()
                    print_response(console, result, current_color)
                    print()
            except Exception as e:
                display.update_stage("Thinking", "error")
                display.finish()
                if active_anim_engine: active_anim_engine.play_spider_error(str(e))
                else: print_spider("ERROR", current_color)
            continue

        if user_input.startswith("/spider"):
            prompt = user_input[len("/spider"):].strip()
            if not prompt: prompt = "What web task do you want Spider-Man to handle?"
            if active_anim_engine: active_anim_engine.play_hero_intro("spider_man")
            from skills.spiderman import SpiderMan
            display.start()
            try:
                result = agent.run(prompt, display, animation=active_anim_engine, active_system_prompt=SpiderMan.SYSTEM_PROMPT)
                display.finish()
                print_spider("SUCCESS", current_color)
                if active_anim_engine and result and "Iron Fist Review" in result: active_anim_engine.play_victory()
                if result:
                    print()
                    print_response(console, result, current_color)
                    print()
            except Exception as e:
                display.update_stage("Thinking", "error")
                display.finish()
                if active_anim_engine: active_anim_engine.play_spider_error(str(e))
                else: print_spider("ERROR", current_color)
            continue

        if user_input.startswith("/iron"):
            prompt = user_input[len("/iron"):].strip()
            if not prompt: prompt = "What code do you want Iron Fist to review?"
            if active_anim_engine: active_anim_engine.play_hero_intro("iron_fist")
            display.start()
            display.update_stage("Classifying", "done", "Skipped (Unified)")
            display.update_stage("Routing", "done", "Iron Fist")
            display.update_stage("Thinking", "running")
            try:
                result = agent.ironfist.review(prompt)
                display.update_stage("Thinking", "done")
                display.finish()
                print_spider("SUCCESS", current_color)
                if active_anim_engine and result and "Iron Fist Review" in result: active_anim_engine.play_victory()
                if result:
                    print()
                    print_response(console, result, current_color)
                    print()
            except Exception as e:
                display.update_stage("Thinking", "error")
                display.finish()
                if active_anim_engine: active_anim_engine.play_spider_error(str(e))
                else: print_spider("ERROR", current_color)
            continue

        if user_input.startswith("/execute"):
            from core.sandbox import Sandbox
            from pathlib import Path
            import os
            
            prompt = user_input[len("/execute"):].strip()
            workspace_dir = Path("workspace")
            files = {}
            if workspace_dir.exists() and workspace_dir.is_dir():
                for p in workspace_dir.rglob("*"):
                    if p.is_file():
                        try:
                            files[str(p.relative_to(workspace_dir))] = p.read_text(encoding="utf-8")
                        except Exception:
                            pass
            
            if not files:
                console.print("[yellow]No files found in workspace/ to execute.[/yellow]")
                continue
                
            # Extract just the first token as entrypoint, ignoring extra conversational text
            entrypoint = prompt.split()[0] if prompt else ""
            
            # If user explicitly typed workspace/file.py, strip the workspace/ part
            if entrypoint.startswith("workspace/") or entrypoint.startswith("workspace\\"):
                entrypoint = entrypoint[10:]

            if not entrypoint:
                if "main.py" in files:
                    entrypoint = "main.py"
                elif "index.js" in files:
                    entrypoint = "index.js"
                else:
                    entrypoint = list(files.keys())[0]
                    console.print(f"[dim]No entrypoint specified. Auto-selected: {entrypoint}[/dim]")
            
            console.print("[dim]Executing in Sandbox...[/dim]")
            sandbox = Sandbox()
            result = sandbox.execute(files, entrypoint)
            
            if sandbox.is_web_server(files):
                if result.get("exit_code", 1) == 0:
                    console.print(Panel(
                        "[bold green]Web server running.[/bold green]\n"
                        "[white]Open[/white] [bold underline]http://localhost:5000[/bold underline] "
                        "[white]in your browser.[/white]",
                        title="🚀 Sandbox Execution",
                        border_style="green"
                    ))
                else:
                    console.print(Panel(
                        result.get("stderr") or "Web server failed to start.",
                        title="❌ Sandbox Error",
                        border_style="red"
                    ))
            else:
                if result.get("exit_code", 1) == 0:
                    console.print(Panel(
                        result.get("stdout", "Execution completed successfully."),
                        title="🚀 Sandbox Execution",
                        border_style="green"
                    ))
                else:
                    console.print(Panel(
                        result.get("stderr", "Execution failed"),
                        title="❌ Sandbox Error",
                        border_style="red"
                    ))
            continue

        if user_input.startswith("/diff"):
            user_input = "Compare files: " + user_input[len("/diff"):].strip()

        print_spider("THINKING", current_color)
        display.start()
        try:
            result = agent.run(user_input, display, animation=active_anim_engine)
            display.finish()
            print_spider("SUCCESS", current_color)
            if active_anim_engine and result and "--- Iron Fist Review ---" in result:
                active_anim_engine.play_victory()
            if result:
                print()
                print_response(console, result, current_color)
                print()
            ch.print_harness_summary(console, harness.last_run())
        except Exception as e:
            display.update_stage("Thinking", "error")
            display.finish()
            if active_anim_engine:
                active_anim_engine.play_spider_error(str(e))
            else:
                print_spider("ERROR", current_color)
                print(f"Error: {e}")

if __name__ == "__main__":
    main()