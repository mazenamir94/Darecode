import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

DAREDEVIL_RED = "#CC0000"
MATT_MURDOCK_BLUE = "#003366"

KAWAII_FACES = ["(｡◕‿◕｡)", "(◕‿◕✿)", "(¬‿¬)", "(>‿<)", "(^‿^)"]
THINKING_VERBS = ["pondering...", "contemplating...", "reasoning...", "evaluating...", "synthesizing..."]

class PipelineDisplay:
    STAGES = [
        "Classifying",
        "Routing",
        "Thinking",
        "Acting",
        "Done",
    ]

    def __init__(self, console: Console, color: str = "#CC0000"):
        self.console = console
        self.color = color
        self.stages = []
        self.live = None
        self._face_idx = 0
        self._verb_idx = 0
        self._start_time = 0.0

        for name in self.STAGES:
            self.stages.append({
                "name": name,
                "status": "pending",
                "elapsed": 0.0,
                "detail": "",
                "start": 0.0,
            })

    def set_color(self, color: str):
        self.color = color

    def start(self):
        for stage in self.stages:
            stage["status"] = "pending"
            stage["elapsed"] = 0.0
            stage["detail"] = ""
            stage["start"] = 0.0
            
        self._start_time = time.time()
        self.live = Live(
            self._render(),
            console=self.console,
            refresh_per_second=8,
            transient=True,
        )
        self.live.__enter__()

    def update_stage(self, stage_name: str, status: str, detail: str = ""):
        for stage in self.stages:
            if stage["name"] == stage_name:
                if status == "running" and stage["status"] != "running":
                    stage["start"] = time.time()
                elif status == "done" and stage["start"] > 0:
                    stage["elapsed"] = time.time() - stage["start"]
                elif status == "skip":
                    stage["status"] = "skip"
                    if self.live:
                        self.live.update(self._render())
                    return

                stage["status"] = status
                if detail:
                    stage["detail"] = detail
                break

        if self.live:
            self.live.update(self._render())

    def pause(self):
        """Temporarily stop Live rendering so input() works cleanly."""
        if self.live:
            try:
                self.live.__exit__(None, None, None)
            except Exception:
                pass

    def resume(self):
        """Restart Live rendering after an input() pause."""
        if self.live:
            self.live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=8,
                transient=True,
            )
            self.live.__enter__()

    def finish(self, summary: str = ""):
        if self.live:
            try:
                self.live.__exit__(None, None, None)
            except Exception:
                pass
            self.live = None

        total = time.time() - self._start_time
        done_count = sum(1 for s in self.stages if s["status"] == "done")
        total_count = sum(1 for s in self.stages if s["status"] != "skip")

        color_rich = self.color
        if color_rich == "#CC0000": color_rich = "red"
        elif color_rich == "#003366": color_rich = "blue"

        msg = summary or f"Completed {done_count}/{total_count} stages"
        self.console.print(
            f"[dim {color_rich}]  {msg} in {total:.1f}s[/dim {color_rich}]"
        )

    def _render(self) -> Panel:
        self._face_idx = (self._face_idx + 1) % len(KAWAII_FACES)
        self._verb_idx = (self._verb_idx + 1) % len(THINKING_VERBS)
        
        face = KAWAII_FACES[self._face_idx]
        verb = THINKING_VERBS[self._verb_idx]
        
        color_rich = self.color
        if color_rich == "#CC0000": color_rich = "red"
        elif color_rich == "#003366": color_rich = "blue"

        lines = Text()
        for stage in self.stages:
            if stage["status"] == "skip":
                continue

            if stage["status"] == "done":
                icon = "[green]✓[/green]"
                name_style = "dim white"
                elapsed = f" [dim]{stage['elapsed']:.1f}s[/dim]"
                active_verb = ""
            elif stage["status"] == "running":
                icon = f"[bold {color_rich}]⠹[/bold {color_rich}]"
                name_style = f"bold {color_rich}"
                running_time = time.time() - stage["start"]
                elapsed = f" [dim]{running_time:.1f}s[/dim]"
                active_verb = f" [dim]· {verb}[/dim]"
            elif stage["status"] == "error":
                icon = "[red]✗[/red]"
                name_style = "red"
                elapsed = f" [dim]{stage['elapsed']:.1f}s[/dim]"
                active_verb = ""
            else:
                icon = "[dim]○[/dim]"
                name_style = "dim"
                elapsed = ""
                active_verb = ""

            detail_text = ""
            if stage["detail"] and stage["status"] in ("running", "done"):
                detail_text = f" [dim]→ {stage['detail']}[/dim]"

            line = f"  {icon} [{name_style}]{stage['name']}[/{name_style}]{detail_text}{active_verb}{elapsed}\n"
            lines.append_text(Text.from_markup(line))

        return Panel(
            lines,
            border_style=color_rich,
            title=f"[bold {color_rich}] {face} DareCode Pipeline [/bold {color_rich}]",
            padding=(0, 1),
            expand=False,
            width=65,
        )
