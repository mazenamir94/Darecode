"""
DareCode ASCII Art Library
All hero art, bug sprites, and fight animation frames.
"""

# ── Daredevil Mask (Dark Mode) ─────────────────────────────────────────────
# Inspired by the Daredevil (Born Again) cowl — V-shaped seam lines,
# angular forehead panels, rectangular eye cutouts, pixel-art style.
DAREDEVIL_MASK = "\n".join([
    "[bold red]              ▄▄██████████▄▄[/bold red]",
    "[bold red]           ▄██████████████████▄[/bold red]",
    "[bold red]         ▄██████████████████████████▄[/bold red]",
    "[bold red]        ██████[/bold red][dark_red]░░[/dark_red][bold red]████████████[/bold red][dark_red]░░[/dark_red][bold red]██████[/bold red]",
    "[bold red]       █████[/bold red][dark_red]░░[/dark_red][bold red]████████████████[/bold red][dark_red]░░[/dark_red][bold red]█████[/bold red]",
    "[bold red]       ████[/bold red][dark_red]░░[/dark_red][bold red]██████████████████[/bold red][dark_red]░░[/dark_red][bold red]████[/bold red]",
    "[bold red]       ████[/bold red][dark_red]░░[/dark_red][bold red]██████[/bold red][dark_red]░░░░░░[/dark_red][bold red]██████[/bold red][dark_red]░░[/dark_red][bold red]████[/bold red]",
    "[bold red]       ███[/bold red]  [red]▀▀▀▀▀▀[/red]  [red]▀▀▀▀▀▀[/red]  [bold red]███[/bold red]",
    "[bold red]       ███[/bold red]  [red]▄▄▄▄▄▄[/red]  [red]▄▄▄▄▄▄[/red]  [bold red]███[/bold red]",
    "[bold red]        ██████████████████████████████[/bold red]",
    "[bold red]          ████████████████████████████[/bold red]",
    "[bold red]             ██████████████████████[/bold red]",
])

# ── Matt Murdock (Light Mode) ──────────────────────────────────────────────
# Clean silhouette — suit, tie, glasses, professional.
MATT_MURDOCK_ART = "\n".join([
    "[bold blue]              ▄▄████████▄▄[/bold blue]",
    "[bold blue]           ▄██████████████████▄[/bold blue]",
    "[bold blue]          ████████████████████████[/bold blue]",
    "[bold blue]         ██████[/bold blue][dim white]▓▓▓▓▓▓▓▓▓▓[/dim white][bold blue]██████[/bold blue]",
    "[bold blue]         █████[/bold blue] [dim white]┌──────────┐[/dim white] [bold blue]█████[/bold blue]",
    "[bold blue]         █████[/bold blue] [dim white]│ [/dim white][bold gold1]●[/bold gold1][dim white]    [/dim white][bold gold1]●[/bold gold1][dim white] │[/dim white] [bold blue]█████[/bold blue]",
    "[bold blue]         █████[/bold blue] [dim white]└──────────┘[/dim white] [bold blue]█████[/bold blue]",
    "[bold blue]          ████[/bold blue]    [dim white]╭──╮[/dim white]    [bold blue]████[/bold blue]",
    "[bold blue]           ███[/bold blue]   [dim white]╰──╯[/dim white]   [bold blue]███[/bold blue]",
    "[bold blue]            ██████████████████[/bold blue]",
    "[bold blue]         ┌──[/bold blue][bold white]▓▓▓▓[/bold white][gold1]████[/gold1][bold white]▓▓▓▓[/bold white][bold blue]──┐[/bold blue]",
    "[bold blue]         │   [/bold blue][bold white]Attorney at Code[/bold white][bold blue]   │[/bold blue]",
])

# ── Jessica Jones ──────────────────────────────────────────────────────────
# Leather jacket, scarf, PI attitude — purple/dark tones.
JESSICA_JONES_ART = "\n".join([
    "[bold purple]              ▄▄████████▄▄[/bold purple]",
    "[bold purple]           ▄██████████████████▄[/bold purple]",
    "[bold purple]          ████████████████████████[/bold purple]",
    "[bold purple]         ██████[/bold purple][dim white]░░░░░░░░░░[/dim white][bold purple]██████[/bold purple]",
    "[bold purple]         █████[/bold purple] [dim white]( ◎    ◎ )[/dim white] [bold purple]█████[/bold purple]",
    "[bold purple]         █████[/bold purple]  [dim white]   ──   [/dim white]  [bold purple]█████[/bold purple]",
    "[bold purple]          ████[/bold purple]  [dim white]  ╰──╯  [/dim white] [bold purple]████[/bold purple]",
    "[bold purple]        ┌─████████████████████████─┐[/bold purple]",
    "[bold purple]        │[/bold purple][dark_red]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/dark_red][bold purple]│[/bold purple]",
    "[bold purple]        │[/bold purple][dim purple] ╔══════════════════════╗ [/dim purple][bold purple]│[/bold purple]",
    "[bold purple]        │[/bold purple][dim purple] ║  ALIAS INVESTIGATIONS║ [/dim purple][bold purple]│[/bold purple]",
    "[bold purple]        └─────────────────────────────┘[/bold purple]",
])

# ── Luke Cage ──────────────────────────────────────────────────────────────
# Hoodie, strong stance, bulletproof — yellow/gold tones.
LUKE_CAGE_ART = "\n".join([
    "[bold yellow]              ▄▄████████▄▄[/bold yellow]",
    "[bold yellow]           ▄██████████████████▄[/bold yellow]",
    "[bold yellow]          ████████████████████████[/bold yellow]",
    "[bold yellow]         ██████[/bold yellow][dim white]░░░░░░░░░░[/dim white][bold yellow]██████[/bold yellow]",
    "[bold yellow]         █████[/bold yellow] [dim white]( ●    ● )[/dim white] [bold yellow]█████[/bold yellow]",
    "[bold yellow]         █████[/bold yellow]  [dim white]   ──   [/dim white]  [bold yellow]█████[/bold yellow]",
    "[bold yellow]          ████[/bold yellow]  [dim white]  ╰══╯  [/dim white] [bold yellow]████[/bold yellow]",
    "[bold yellow]       ┌──████████████████████████──┐[/bold yellow]",
    "[bold yellow]       │[/bold yellow][gold1]  ████████████████████████  [/gold1][bold yellow]│[/bold yellow]",
    "[bold yellow]       │[/bold yellow][gold1]  ██ SWEET CHRISTMAS!  ██  [/gold1][bold yellow]│[/bold yellow]",
    "[bold yellow]       │[/bold yellow][gold1]  ████████████████████████  [/gold1][bold yellow]│[/bold yellow]",
    "[bold yellow]       └──────────────────────────────┘[/bold yellow]",
])

# ── Iron Fist ──────────────────────────────────────────────────────────────
# Glowing fist, martial arts — green/gold tones.
IRON_FIST_ART = "\n".join([
    "[bold green]              ▄▄████████▄▄[/bold green]",
    "[bold green]           ▄██████████████████▄[/bold green]",
    "[bold green]          ████████████████████████[/bold green]",
    "[bold green]         ██████[/bold green][dim white]░░░░░░░░░░[/dim white][bold green]██████[/bold green]",
    "[bold green]         █████[/bold green] [dim white]( ◉    ◉ )[/dim white] [bold green]█████[/bold green]",
    "[bold green]         █████[/bold green]  [dim white]   ──   [/dim white]  [bold green]█████[/bold green]",
    "[bold green]          ████[/bold green]  [dim white]  ╰──╯  [/dim white] [bold green]████[/bold green]",
    "[bold green]           ███████████████████████[/bold green]",
    "[bold bright_green]         ╔═══╗[/bold bright_green]",
    "[bold bright_green]         ║ ✊ ║[/bold bright_green][bold green]  ═══ [/bold green][bold yellow]CHI FOCUSED[/bold yellow]",
    "[bold bright_green]         ╚═══╝[/bold bright_green][bold green]  ═══ [/bold green][bold yellow]CODE REFINED[/bold yellow]",
    "[bold green]       ══════════════════════════════[/bold green]",
])

# ── Spider-Man ─────────────────────────────────────────────────────────────
# Web pattern mask, quippy — red/blue tones.
SPIDER_MAN_ART = "\n".join([
    "[bold red]              ▄▄████████▄▄[/bold red]",
    "[bold red]           ▄██[/bold red][blue]╲╲╲[/blue][bold red]████[/bold red][blue]╱╱╱[/blue][bold red]██▄[/bold red]",
    "[bold red]         ████[/bold red][blue]╲╲[/blue][bold red]████████[/bold red][blue]╱╱[/blue][bold red]████[/bold red]",
    "[bold red]        █████[/bold red][blue]╲[/blue][bold red]██[/bold red][white]◈[/white][bold red]████[/bold red][white]◈[/white][bold red]██[/bold red][blue]╱[/blue][bold red]█████[/bold red]",
    "[bold red]       ██████[/bold red][blue]╲[/blue][bold red]██████████[/bold red][blue]╱[/blue][bold red]██████[/bold red]",
    "[bold red]       ███████[/bold red][blue]╲╲[/blue][bold red]██████[/bold red][blue]╱╱[/blue][bold red]███████[/bold red]",
    "[bold red]        ███████[/bold red][blue]╲╲[/blue][bold red]████[/bold red][blue]╱╱[/blue][bold red]███████[/bold red]",
    "[bold red]         ████████[/bold red][blue]╲╲╱╱[/blue][bold red]████████[/bold red]",
    "[bold red]          ██████████████████████[/bold red]",
    "[blue]         ╱╲╱╲╱╲[/blue][bold red]████████[/bold red][blue]╱╲╱╲╱╲[/blue]",
    "[blue]       ─── [/blue][bold white]Your friendly neighborhood[/bold white][blue] ───[/blue]",
    "[blue]       ─── [/blue][bold white]   web developer       [/bold white][blue] ───[/blue]",
])


# ── Bug Sprites ────────────────────────────────────────────────────────────

BUG_ICON = "\n".join([
    "[bold green]  ╔═══╗ [/bold green]",
    "[bold green]  ║BUG║ [/bold green]",
    "[bold green] ╱║   ║╲[/bold green]",
    "[bold green]  ╚═══╝ [/bold green]",
])

BUG_DEAD = "\n".join([
    "[dim red]  ╔═══╗ [/dim red]",
    "[dim red]  ║X_X║ [/dim red]",
    "[dim red]  ║   ║ [/dim red]",
    "[dim red]  ╚═══╝ [/dim red]",
])

BUG_SWARM = "\n".join([
    "[bold green] ╔═╗  ╔═╗  ╔═╗[/bold green]",
    "[bold green] ║B║  ║U║  ║G║[/bold green]",
    "[bold green] ╚═╝  ╚═╝  ╚═╝[/bold green]",
])


# ── Fight Animation Frames ────────────────────────────────────────────────
# Each hero has 4 frames. Displayed side-by-side with bug sprite.

DAREDEVIL_FIGHT = [
    # Frame 1: Ready stance
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [bold green]╔═══╗[/bold green]",
        "[bold red]   ║D║  ──    [/bold red]   [dim]>>>>[/dim]     [bold green]║BUG║[/bold green]",
        "[bold red]  ╱║ ║╲       [/bold red]              [bold green]║   ║[/bold green]",
        "[bold red]   ╚═╝        [/bold red]              [bold green]╚═══╝[/bold green]",
    ]),
    # Frame 2: Throwing billy club
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [bold green]╔═══╗[/bold green]",
        "[bold red]   ║D║──━━━━━━━━━━━━━━━━►[/bold red]  [bold green]║BUG║[/bold green]",
        "[bold red]  ╱║ ║╲       [/bold red]              [bold green]║   ║[/bold green]",
        "[bold red]   ╚═╝        [/bold red]              [bold green]╚═══╝[/bold green]",
    ]),
    # Frame 3: Impact
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]           [bold yellow]💥[/bold yellow][bold green]╔═══╗[/bold green]",
        "[bold red]   ║D║  ──    [/bold red]   [bold yellow]CRACK![/bold yellow] [yellow]║BUG║[/yellow]",
        "[bold red]  ╱║ ║╲       [/bold red]           [bold yellow]💥[/bold yellow][yellow]║ ╳ ║[/yellow]",
        "[bold red]   ╚═╝        [/bold red]              [yellow]╚═══╝[/yellow]",
    ]),
    # Frame 4: Victory
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [dim red]╔═══╗[/dim red]",
        "[bold red]   ║D║ ✓      [/bold red]   [green]FIXED![/green]  [dim red]║X_X║[/dim red]",
        "[bold red]  ╱║ ║╲       [/bold red]              [dim red]║   ║[/dim red]",
        "[bold red]   ╚═╝        [/bold red]              [dim red]╚═══╝[/dim red]",
    ]),
]

JESSICA_JONES_FIGHT = [
    "\n".join([
        "[bold purple]   ╔═╗        [/bold purple]              [bold green]╔═══╗[/bold green]",
        "[bold purple]   ║J║  🔍    [/bold purple]   [dim]>>>>[/dim]     [bold green]║BUG║[/bold green]",
        "[bold purple]  ╱║ ║╲       [/bold purple]              [bold green]║   ║[/bold green]",
        "[bold purple]   ╚═╝        [/bold purple]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold purple]   ╔═╗        [/bold purple]              [bold green]╔═══╗[/bold green]",
        "[bold purple]   ║J║━━🔍━━━━━━━━━━━━━►[/bold purple]  [bold green]║BUG║[/bold green]",
        "[bold purple]  ╱║ ║╲       [/bold purple]              [bold green]║   ║[/bold green]",
        "[bold purple]   ╚═╝        [/bold purple]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold purple]   ╔═╗        [/bold purple]           [bold yellow]💥[/bold yellow][bold green]╔═══╗[/bold green]",
        "[bold purple]   ║J║  👊    [/bold purple]   [bold yellow]FOUND![/bold yellow] [yellow]║BUG║[/yellow]",
        "[bold purple]  ╱║ ║╲       [/bold purple]           [bold yellow]💥[/bold yellow][yellow]║ ╳ ║[/yellow]",
        "[bold purple]   ╚═╝        [/bold purple]              [yellow]╚═══╝[/yellow]",
    ]),
    "\n".join([
        "[bold purple]   ╔═╗        [/bold purple]              [dim red]╔═══╗[/dim red]",
        "[bold purple]   ║J║ ✓      [/bold purple]   [green]TRACED![/green] [dim red]║X_X║[/dim red]",
        "[bold purple]  ╱║ ║╲       [/bold purple]              [dim red]║   ║[/dim red]",
        "[bold purple]   ╚═╝        [/bold purple]              [dim red]╚═══╝[/dim red]",
    ]),
]

LUKE_CAGE_FIGHT = [
    "\n".join([
        "[bold yellow]   ╔═╗        [/bold yellow]              [bold green]╔═══╗[/bold green]",
        "[bold yellow]   ║L║  💪    [/bold yellow]   [dim]>>>>[/dim]     [bold green]║BUG║[/bold green]",
        "[bold yellow]  ╱║ ║╲       [/bold yellow]              [bold green]║   ║[/bold green]",
        "[bold yellow]   ╚═╝        [/bold yellow]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold yellow]   ╔═╗        [/bold yellow]              [bold green]╔═══╗[/bold green]",
        "[bold yellow]   ║L║━━💪━━━━━━━━━━━━━►[/bold yellow]  [bold green]║BUG║[/bold green]",
        "[bold yellow]  ╱║ ║╲       [/bold yellow]              [bold green]║   ║[/bold green]",
        "[bold yellow]   ╚═╝        [/bold yellow]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold yellow]   ╔═╗        [/bold yellow]           [bold yellow]💥[/bold yellow][bold green]╔═══╗[/bold green]",
        "[bold yellow]   ║L║  💪    [/bold yellow]   [bold yellow]SMASH![/bold yellow] [yellow]║BUG║[/yellow]",
        "[bold yellow]  ╱║ ║╲       [/bold yellow]           [bold yellow]💥[/bold yellow][yellow]║ ╳ ║[/yellow]",
        "[bold yellow]   ╚═╝        [/bold yellow]              [yellow]╚═══╝[/yellow]",
    ]),
    "\n".join([
        "[bold yellow]   ╔═╗        [/bold yellow]              [dim red]╔═══╗[/dim red]",
        "[bold yellow]   ║L║ ✓      [/bold yellow]  [green]CRUSHED![/green] [dim red]║X_X║[/dim red]",
        "[bold yellow]  ╱║ ║╲       [/bold yellow]              [dim red]║   ║[/dim red]",
        "[bold yellow]   ╚═╝        [/bold yellow]              [dim red]╚═══╝[/dim red]",
    ]),
]

IRON_FIST_FIGHT = [
    "\n".join([
        "[bold green]   ╔═╗        [/bold green]              [bold green]╔═══╗[/bold green]",
        "[bold green]   ║I║  ✊    [/bold green]   [dim]>>>>[/dim]     [bold green]║BUG║[/bold green]",
        "[bold green]  ╱║ ║╲       [/bold green]              [bold green]║   ║[/bold green]",
        "[bold green]   ╚═╝        [/bold green]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold green]   ╔═╗        [/bold green]              [bold green]╔═══╗[/bold green]",
        "[bold bright_green]   ║I║━━✊━━━━━━━━━━━━━►[/bold bright_green]  [bold green]║BUG║[/bold green]",
        "[bold green]  ╱║ ║╲       [/bold green]              [bold green]║   ║[/bold green]",
        "[bold green]   ╚═╝        [/bold green]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold green]   ╔═╗        [/bold green]           [bold yellow]💥[/bold yellow][bold green]╔═══╗[/bold green]",
        "[bold bright_green]   ║I║  ✊    [/bold bright_green]   [bold yellow]STRIKE![/bold yellow][yellow]║BUG║[/yellow]",
        "[bold green]  ╱║ ║╲       [/bold green]           [bold yellow]💥[/bold yellow][yellow]║ ╳ ║[/yellow]",
        "[bold green]   ╚═╝        [/bold green]              [yellow]╚═══╝[/yellow]",
    ]),
    "\n".join([
        "[bold green]   ╔═╗        [/bold green]              [dim red]╔═══╗[/dim red]",
        "[bold bright_green]   ║I║ ✓      [/bold bright_green] [green]REFINED![/green] [dim red]║X_X║[/dim red]",
        "[bold green]  ╱║ ║╲       [/bold green]              [dim red]║   ║[/dim red]",
        "[bold green]   ╚═╝        [/bold green]              [dim red]╚═══╝[/dim red]",
    ]),
]

SPIDER_MAN_FIGHT = [
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [bold green]╔═══╗[/bold green]",
        "[bold red]   ║S║  🕸     [/bold red]   [dim]>>>>[/dim]     [bold green]║BUG║[/bold green]",
        "[bold red]  ╱║ ║╲       [/bold red]              [bold green]║   ║[/bold green]",
        "[bold red]   ╚═╝        [/bold red]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [bold green]╔═══╗[/bold green]",
        "[bold red]   ║S║━━🕸━━━━━━━━━━━━━►[/bold red]   [bold green]║BUG║[/bold green]",
        "[bold red]  ╱║ ║╲       [/bold red]              [bold green]║   ║[/bold green]",
        "[bold red]   ╚═╝        [/bold red]              [bold green]╚═══╝[/bold green]",
    ]),
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]           [bold yellow]💥[/bold yellow][bold green]╔═══╗[/bold green]",
        "[bold red]   ║S║  🕸     [/bold red]   [bold yellow]WEBBED![/bold yellow][yellow]║BUG║[/yellow]",
        "[bold red]  ╱║ ║╲       [/bold red]           [bold yellow]💥[/bold yellow][yellow]║ ╳ ║[/yellow]",
        "[bold red]   ╚═╝        [/bold red]              [yellow]╚═══╝[/yellow]",
    ]),
    "\n".join([
        "[bold red]   ╔═╗        [/bold red]              [dim red]╔═══╗[/dim red]",
        "[bold red]   ║S║ ✓      [/bold red]  [green]SHIPPED![/green] [dim red]║X_X║[/dim red]",
        "[bold red]  ╱║ ║╲       [/bold red]              [dim red]║   ║[/dim red]",
        "[bold red]   ╚═╝        [/bold red]              [dim red]╚═══╝[/dim red]",
    ]),
]


# ── Team Assembly Banner ───────────────────────────────────────────────────

DEFENDERS_BANNER = "\n".join([
    "[bold white]",
    "  ████████╗██╗  ██╗███████╗",
    "  ╚══██╔══╝██║  ██║██╔════╝",
    "     ██║   ███████║█████╗  ",
    "     ██║   ██╔══██║██╔══╝  ",
    "     ██║   ██║  ██║███████╗",
    "     ╚═╝   ╚═╝  ╚═╝╚══════╝",
    "[/bold white]",
    "[bold red]  ██████╗ ███████╗███████╗███████╗███╗   ██╗██████╗ ███████╗██████╗ ███████╗[/bold red]",
    "[bold red]  ██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗██╔════╝[/bold red]",
    "[bold red]  ██║  ██║█████╗  █████╗  █████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝███████╗[/bold red]",
    "[bold red]  ██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗╚════██║[/bold red]",
    "[bold red]  ██████╔╝███████╗██║     ███████╗██║ ╚████║██████╔╝███████╗██║  ██║███████║[/bold red]",
    "[bold red]  ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝[/bold red]",
])

TEAM_ASSEMBLED = "\n".join([
    "",
    "[bold white]  ═══════════════════════════════════════════════[/bold white]",
    "[bold red]     ██████╗  ███████╗ █████╗  ██████╗ ██╗   ██╗[/bold red]",
    "[bold red]     ██╔══██╗ ██╔════╝██╔══██╗ ██╔══██╗╚██╗ ██╔╝[/bold red]",
    "[bold red]     ██████╔╝ █████╗  ███████║ ██║  ██║ ╚████╔╝ [/bold red]",
    "[bold red]     ██╔══██╗ ██╔══╝  ██╔══██║ ██║  ██║  ╚██╔╝  [/bold red]",
    "[bold red]     ██║  ██║ ███████╗██║  ██║ ██████╔╝   ██║   [/bold red]",
    "[bold red]     ╚═╝  ╚═╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   [/bold red]",
    "[bold white]  ═══════════════════════════════════════════════[/bold white]",
    "",
])

VICTORY_BANNER = "\n".join([
    "",
    "[bold green]  ╔══════════════════════════════════════╗[/bold green]",
    "[bold green]  ║     ✓  MISSION ACCOMPLISHED  ✓      ║[/bold green]",
    "[bold green]  ║      All bugs have been defeated     ║[/bold green]",
    "[bold green]  ╚══════════════════════════════════════╝[/bold green]",
    "",
])


# ── Billy Club Loading Animation ───────────────────────────────────────────
# Daredevil's iconic billy club spinning while loading/processing.

BILLY_CLUB_FRAMES = [
    "\n".join([
        "[bold red]     ╱[/bold red]",
        "[bold red]    ╱ [/bold red]    [dim]Loading…[/dim]",
        "[bold red]   ╱  [/bold red]",
        "[bold red]  ●   [/bold red]",
    ]),
    "\n".join([
        "[bold red]       [/bold red]",
        "[bold red]  ━━━━●[/bold red]  [dim]Loading…[/dim]",
        "[bold red]       [/bold red]",
        "[bold red]       [/bold red]",
    ]),
    "\n".join([
        "[bold red]  ●   [/bold red]",
        "[bold red]   ╲  [/bold red]    [dim]Loading…[/dim]",
        "[bold red]    ╲ [/bold red]",
        "[bold red]     ╲[/bold red]",
    ]),
    "\n".join([
        "[bold red]       [/bold red]",
        "[bold red]  ●━━━━[/bold red]  [dim]Loading…[/dim]",
        "[bold red]       [/bold red]",
        "[bold red]       [/bold red]",
    ]),
    "\n".join([
        "[bold red]     ╱[/bold red]",
        "[bold red]    ╱ [/bold red]    [bold red]Striking…[/bold red]",
        "[bold red]   ╱  [/bold red]",
        "[bold red]  ●   [/bold red]",
    ]),
    "\n".join([
        "[bold red]       [/bold red]",
        "[bold red]  ━━━━●[/bold red]  [bold red]Striking…[/bold red]",
        "[bold red]       [/bold red]",
        "[bold red]       [/bold red]",
    ]),
    "\n".join([
        "[bold red]  ●   [/bold red]",
        "[bold red]   ╲  [/bold red]    [bold yellow]Impact![/bold yellow]",
        "[bold red]    ╲ [/bold red]",
        "[bold red]     ╲[/bold red]",
    ]),
    "\n".join([
        "[bold red]       [/bold red]",
        "[bold red]  ●━━━━[/bold red]  [bold green]Ready.[/bold green]",
        "[bold red]       [/bold red]",
        "[bold red]       [/bold red]",
    ]),
]

# Matt Murdock's gavel loading (light mode)
GAVEL_FRAMES = [
    "\n".join([
        "[bold blue]      ╱█╲[/bold blue]",
        "[bold blue]     ╱ █ ╲[/bold blue]   [dim]Reviewing…[/dim]",
        "[bold blue]    ╱  █  ╲[/bold blue]",
        "[bold blue]  ════════════[/bold blue]",
    ]),
    "\n".join([
        "[bold blue]       █[/bold blue]",
        "[bold blue]       █[/bold blue]     [dim]Reviewing…[/dim]",
        "[bold blue]       █[/bold blue]",
        "[bold blue]  ════════════[/bold blue]",
    ]),
    "\n".join([
        "[bold blue]         [/bold blue]",
        "[bold blue]     █████[/bold blue]   [bold blue]Examining…[/bold blue]",
        "[bold blue]       █[/bold blue]",
        "[bold blue]  ════════════[/bold blue]",
    ]),
    "\n".join([
        "[bold blue]      ╱█╲[/bold blue]",
        "[bold blue]     ╱ █ ╲[/bold blue]   [bold yellow]Order![/bold yellow]",
        "[bold blue]  ═══╱══█══╲═══[/bold blue]",
        "[bold blue]  [bold yellow]💥[/bold yellow]════════════[bold yellow]💥[/bold yellow][/bold blue]",
    ]),
]


# ── Coffee Break Art ──────────────────────────────────────────────────────

COFFEE_ART = "\n".join([
    "[bold white]        ( ([/bold white]",
    "[bold white]         ) )[/bold white]",
    "[bold white]       ........[/bold white]",
    "[bold white]       |      |][/bold white]",
    "[bold white]       |  [/bold white][bold yellow]DD[/bold yellow][bold white]  |][/bold white]",
    "[bold white]       |      |][/bold white]",
    "[bold white]        `----'[/bold white]",
    "[dim]    Josie's Bar[/dim]",
])


# ── Spider Companion Frames ───────────────────────────────────────────────
# Persistent animated spider that lives above the prompt field.
# Each state has a list of compact frames (2-3 lines, ~30 chars wide).

SPIDER_FRAMES = {
    "idle": [
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red] ╲[bold bright_red]▄███▄[/bold bright_red][red]╱[/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]▀ ▀[/bold white][bold bright_red]█[/bold bright_red][/red]",
            "[red] ╱[bold bright_red]▀███▀[/bold bright_red][red]╲[/red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red][/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]▀ ▀[/bold white][bold bright_red]█[/bold bright_red][/red]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red][/red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red] ╱[bold bright_red]▄███▄[/bold bright_red][red]╲[/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]▀ ▀[/bold white][bold bright_red]█[/bold bright_red][/red]",
            "[red] ╲[bold bright_red]▀███▀[/bold bright_red][red]╱[/red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red][/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]─ ─[/bold white][bold bright_red]█[/bold bright_red][/red]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red][/red]",
        ]),
    ],
    "error": [
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red] [bold yellow]⚠[/bold yellow]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]X X[/bold white][bold bright_red]█[/bold bright_red]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red] [bold yellow]⚠⚠[/bold yellow]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]! ![/bold white][bold bright_red]█[/bold bright_red]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red] ╲[bold bright_red]▄███▄[/bold bright_red][red]╱[/red] [bold yellow]!!![/bold yellow]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]X X[/bold white][bold bright_red]█[/bold bright_red]",
            "[red] ╱[bold bright_red]▀███▀[/bold bright_red][red]╲[/red]",
        ]),
    ],
    "thinking": [
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red] ╲[bold bright_red]▄███▄[/bold bright_red][red]╱[/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]° °[/bold white][bold bright_red]█[/bold bright_red] [dim].[/dim]",
            "[red] ╱[bold bright_red]▀███▀[/bold bright_red][red]╲[/red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]° °[/bold white][bold bright_red]█[/bold bright_red] [dim]..[/dim]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red] ╲[bold bright_red]▄███▄[/bold bright_red][red]╱[/red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]° °[/bold white][bold bright_red]█[/bold bright_red] [dim]...[/dim]",
            "[red] ╱[bold bright_red]▀███▀[/bold bright_red][red]╲[/red]",
        ]),
        "\n".join([
            "[dark_red]    ║[/dark_red]",
            "[red]  [bold bright_red]▄███▄[/bold bright_red]",
            "[red]  [bold bright_red]█[/bold bright_red][bold white]° °[/bold white][bold bright_red]█[/bold bright_red] [dim]?[/dim]",
            "[red]  [bold bright_red]▀███▀[/bold bright_red]",
        ]),
    ],
}

WEB_TANGLED_ART = "\n".join([
    "[blue]    ╱╲  ╱╲  ╱╲  ╱╲  ╱╲[/blue]",
    "[blue]   ╱  ╲╱  ╲╱  ╲╱  ╲╱  ╲[/blue]",
    "[blue]  ╱    ╲    ╲    ╲    ╲  ╲[/blue]",
    "[bold red]  ╲   /●\\  [/bold red][bold yellow]⚠ ERROR ⚠[/bold yellow][bold red]   ╱[/bold red]",
    "[blue]   ╲  ╱╲  ╱╲  ╱╲  ╱╲  ╱[/blue]",
    "[blue]    ╲╱  ╲╱  ╲╱  ╲╱  ╲╱[/blue]",
])


# ── Mapping for easy lookup ────────────────────────────────────────────────

HERO_ART = {
    "daredevil": DAREDEVIL_MASK,
    "matt_murdock": MATT_MURDOCK_ART,
    "jessica_jones": JESSICA_JONES_ART,
    "luke_cage": LUKE_CAGE_ART,
    "iron_fist": IRON_FIST_ART,
    "spider_man": SPIDER_MAN_ART,
}

HERO_FIGHT_FRAMES = {
    "daredevil": DAREDEVIL_FIGHT,
    "jessica_jones": JESSICA_JONES_FIGHT,
    "luke_cage": LUKE_CAGE_FIGHT,
    "iron_fist": IRON_FIST_FIGHT,
    "spider_man": SPIDER_MAN_FIGHT,
}
