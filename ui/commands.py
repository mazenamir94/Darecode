from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style

from ui.theme import DAREDEVIL_RED

COMMANDS = [
    ("/mode", "Toggle Matt Murdock / Daredevil themes"),
    ("/coffee", "Casual chat mode"),
    ("/explain", "Explain code (single-shot)"),
    ("/review", "Review code (single-shot)"),
    ("/plan", "Create an implementation plan (single-shot)"),
    ("/diff", "Compare files (ReAct loop)"),
    ("/jessica", "Debug specialist"),
    ("/luke", "Backend specialist"),
    ("/spider", "Web specialist"),
    ("/iron", "Code Review specialist (single-shot)"),
    ("/defenders", "Assemble team for subtask execution"),
    ("/execute", "Run code in Docker sandbox (auto-detects web apps)"),
    ("/test", "Generate (and optionally run) tests for the last code"),
    ("/snippet", "Save the last code as a named snippet"),
    ("/stats", "Show session statistics"),
    ("/history", "Show conversation history summary"),
    ("/harness", "Agent observability: /harness on|off|show|summary"),
    ("/server", "Web servers: /server start|stop|list [name]"),
    ("/project", "Workspace projects: /project list|use <name>"),
    ("/team", "Defenders auto-mode: /team on|off"),
    ("/model", "Switch Bedrock model: /model <alias|id>"),
    ("/change api", "Change Bedrock credentials at runtime"),
    ("/clear", "Clear the screen and reprint the header"),
    ("/save", "Save current session"),
    ("/sessions", "List and load saved sessions"),
    ("/exit", "Exit DareCode"),
]

class SlashCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lstrip()
        if not text.startswith("/"):
            return
        lower = text.lower()
        for cmd, desc in COMMANDS:
            if cmd.startswith(lower):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta=desc,
                )

def get_prompt_session(color: str = DAREDEVIL_RED) -> PromptSession:
    style = Style.from_dict({
        "prompt": f"bold {color}",
        "completion-menu": "bg:#16213e #cccccc",
        "completion-menu.completion": "bg:#16213e #cccccc",
        "completion-menu.completion.current": f"bg:{color} #ffffff bold",
        "completion-menu.meta": "bg:#16213e #777777",
        "completion-menu.meta.current": f"bg:{color} #eeeeee",
    })
    
    return PromptSession(
        completer=SlashCompleter(),
        style=style,
        complete_while_typing=True
    )
