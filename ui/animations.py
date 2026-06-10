"""
DareCode Animation Engine
Uses Rich Live for smooth terminal animations during processing.
"""

import time
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align

from ui.ascii_art import (
    HERO_ART, HERO_FIGHT_FRAMES, DEFENDERS_BANNER,
    TEAM_ASSEMBLED, VICTORY_BANNER,
    BILLY_CLUB_FRAMES, GAVEL_FRAMES, COFFEE_ART,
    SPIDER_FRAMES, WEB_TANGLED_ART,
)
from ui.personas import Persona


HERO_COLORS = {
    "daredevil": "red",
    "jessica_jones": "purple",
    "luke_cage": "yellow",
    "iron_fist": "green",
    "spider_man": "red",
}

HERO_NAMES = {
    "daredevil": "Daredevil",
    "jessica_jones": "Jessica Jones",
    "luke_cage": "Luke Cage",
    "iron_fist": "Iron Fist",
    "spider_man": "Spider-Man",
}

HERO_ROLES = {
    "daredevil": "Leading The Charge",
    "jessica_jones": "Investigating The Bug",
    "luke_cage": "Heavy Lifting",
    "iron_fist": "Refining The Code",
    "spider_man": "Spinning The Web",
}


class AnimationEngine:
    """Plays hero fight animations and team assembly sequences."""

    def __init__(self, console: Console, persona: Persona):
        self.console = console
        self.persona = persona

    def play_fight(self, hero: str = "daredevil", duration: float = 2.0):
        """
        Play a hero fight animation during processing.
        Shows 4 frames of the hero defeating a bug.
        """
        frames = HERO_FIGHT_FRAMES.get(hero, HERO_FIGHT_FRAMES.get("daredevil"))
        if not frames:
            return

        color = HERO_COLORS.get(hero, self.persona.color_primary)
        name = HERO_NAMES.get(hero, "DareCode")
        role = HERO_ROLES.get(hero, "Processing")

        frame_time = duration / len(frames)

        try:
            with Live(console=self.console, refresh_per_second=4, transient=True) as live:
                for frame in frames:
                    panel = Panel(
                        Text.from_markup(frame),
                        border_style=color,
                        title=f"[bold {color}]  {name} — {role}[/bold {color}]",
                        padding=(0, 1),
                    )
                    live.update(panel)
                    time.sleep(frame_time)
        except Exception:
            pass

    def play_team_assembly(self, defenders: List[str]):
        """
        Epic team assembly sequence.
        Shows banner, then each hero's intro card.
        """
        self.console.print()
        self.console.print(Text.from_markup(DEFENDERS_BANNER))
        self.console.print()

        for codename in defenders:
            name = HERO_NAMES.get(codename, codename)
            color = HERO_COLORS.get(codename, "white")
            role = HERO_ROLES.get(codename, "Support")
            art = HERO_ART.get(codename, "")

            if art:
                self.console.print(Panel(
                    Text.from_markup(art),
                    border_style=color,
                    title=f"[bold {color}]  {name} — {role}[/bold {color}]",
                    subtitle=f"[dim {color}]REPORTING FOR DUTY[/dim {color}]",
                    padding=(0, 1),
                ))
                time.sleep(0.6)

        self.console.print(Text.from_markup(TEAM_ASSEMBLED))

    def play_hero_intro(self, codename: str):
        """Single hero introduction card."""
        name = HERO_NAMES.get(codename, codename)
        color = HERO_COLORS.get(codename, "white")
        role = HERO_ROLES.get(codename, "Support")
        art = HERO_ART.get(codename, "")

        if art:
            self.console.print(Panel(
                Text.from_markup(art),
                border_style=color,
                title=f"[bold {color}]  {name}[/bold {color}]",
                subtitle=f"[dim {color}]{role}[/dim {color}]",
                padding=(0, 1),
            ))

    def play_victory(self):
        """Task completion celebration."""
        self.console.print(Text.from_markup(VICTORY_BANNER))

    def play_hero_working(self, codename: str):
        """Show a brief fight animation for a specific Defender working."""
        self.play_fight(hero=codename, duration=1.5)

    def play_billy_club_loading(self, message: str = ""):
        """
        Play the iconic billy club spinning animation while loading.
        Uses Daredevil's billy club in dark mode, gavel in light mode.
        """
        frames = BILLY_CLUB_FRAMES if self.persona.mode == "dark" else GAVEL_FRAMES
        color = self.persona.color_primary
        title = "Daredevil" if self.persona.mode == "dark" else "Matt Murdock"

        try:
            with Live(console=self.console, refresh_per_second=4, transient=True) as live:
                for cycle in range(2):
                    for frame in frames:
                        display = frame
                        if message:
                            display = frame + f"\n  [dim]{message}[/dim]"
                        panel = Panel(
                            Text.from_markup(display),
                            border_style=color,
                            title=f"[bold {color}]  {title}[/bold {color}]",
                            padding=(0, 1),
                            width=40,
                        )
                        live.update(panel)
                        time.sleep(0.25)
        except Exception:
            pass

    def play_coffee_break(self):
        """Show the coffee break art for /coffee mode."""
        color = self.persona.color_primary
        self.console.print(Panel(
            Text.from_markup(COFFEE_ART),
            border_style=color,
            title=f"[bold {color}]  Coffee Break — Josie's Bar[/bold {color}]",
            subtitle=f"[dim {color}]Talk about anything. Type /back to return.[/dim {color}]",
            padding=(1, 2),
        ))

    def play_spider_error(self, error_msg: str = ""):
        """Spider drops down alarmed, then show error panel."""
        error_frames = SPIDER_FRAMES.get("error", [])
        try:
            with Live(console=self.console, refresh_per_second=4, transient=True) as live:
                for frame in error_frames:
                    panel = Panel(
                        Text.from_markup(frame),
                        border_style="red",
                        title="[bold red]  Spider-Man — Incoming![/bold red]",
                        padding=(0, 1),
                        width=45,
                    )
                    live.update(panel)
                    time.sleep(0.3)
        except Exception:
            pass

        msg = error_msg or "Something went wrong with the API!"
        self.console.print(Panel(
            Text.from_markup(
                f"{WEB_TANGLED_ART}\n\n"
                f"[bold red]{msg}[/bold red]\n\n"
                "[dim]Available offline commands:[/dim]\n"
                "[bold white]  /coffee[/bold white]  [dim]Chat at Josie's Bar[/dim]\n"
                "[bold white]  /help[/bold white]    [dim]Show all commands[/dim]\n"
                "[bold white]  /stats[/bold white]   [dim]Session statistics[/dim]\n"
                "[bold white]  /history[/bold white] [dim]Conversation history[/dim]\n"
                "[bold white]  /diff[/bold white]    [dim]Compare last runs[/dim]\n"
                "[bold white]  /snippet[/bold white] [dim]Save code snippets[/dim]"
            ),
            border_style="red",
            title="[bold red]  ⚠ Spidey-Sense Alert ⚠[/bold red]",
            padding=(1, 2),
        ))
