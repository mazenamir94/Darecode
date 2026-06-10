import os
import json
from ui.personas import DAREDEVIL
from core.tools import run_tool, set_display, TOOL_SPECS
from core.harnesses import harness

class Agent:
    def __init__(self):
        from core.brain import Brain
        self.brain = Brain()
        self.history = []
        self.written_files = {}

        # Session-level metrics for /stats (monotonic, not evicted like harness runs).
        self.metrics = {
            "requests": 0,
            "llm_calls": 0,
            "tool_calls": 0,
            "tool_successes": 0,
            "tool_failures": 0,
            "files_written": 0,
        }
        # Last run's written files (path -> content), retained for /test and /snippet.
        self.last_run_files = {}
        # Active project (set by /project use); influences run() + /server default.
        self.current_project = None
        self.current_project_dir = None

        # Default system prompt for the main DareCode agent
        self.system_prompt = """You are DareCode v2.0, an autonomous AI coding assistant.
You complete coding tasks by calling the tools that are provided to you.

You have these tools available:
- bash(command, timeout=30) - run a shell command.
- glob(pattern, base_dir=".") - find files.
- file_read(path) - read a file.
- grep(pattern, path, case_sensitive=True) - search in a file.
- write_file(path, content) - create or overwrite a file.
- file_edit(path, old_text, new_text) - surgically replace text in a file.

CRITICAL RULES:
- Do ALL real work by calling tools. Never claim that you created or edited a file, or
  report command output, unless a tool call actually returned that result.
- Always read a file before editing it; never invent file contents.
- Work step by step: call one or more tools, look at the results, then continue.
- When the task is fully complete, stop calling tools and give a short final summary.
- Never explore endlessly. If you are stuck, say so and ask the user.

WORKSPACE RULES:
- ALL your work (creating files, reading files, executing commands) MUST take place inside the `workspace/` directory by default.
- DO NOT modify, delete, or read files outside of `workspace/` (like main.py, core/, skills/) UNLESS the user explicitly commands you to.
- It is perfectly okay for you to delete or modify any files that are INSIDE the `workspace/` directory.

PROJECT STRUCTURE RULES:
- For any task that produces more than a single throwaway script, create a dedicated project
  folder `workspace/<project-name>/` and organize files into a conventional, maintainable layout
  for the stack. Examples:
    - Flask:   `workspace/<name>/app.py`, `templates/`, `static/`, `requirements.txt`, `README.md`
    - Express: `workspace/<name>/package.json`, `src/`, `public/`, `README.md`
    - Python:  `workspace/<name>/main.py`, module files, `README.md`
- A single one-off script may live directly at `workspace/` root.
- If the user asks you to build somewhere OUTSIDE `workspace/`, the write will prompt for the
  user's permission first; once approved, build the SAME structured project layout at that path.
"""

        from skills.ironfist import IronFist
        self.ironfist = IronFist(self.brain)

    def run(self, user_input: str, display=None, animation=None, active_system_prompt=None) -> str:
        set_display(display)

        if active_system_prompt is None:
            active_system_prompt = self.system_prompt

        # If a project is active, steer all work into its directory.
        if self.current_project_dir:
            active_system_prompt += (
                f"\n\nACTIVE PROJECT: The current project directory is "
                f"`{self.current_project_dir}`. Put all new work there unless told otherwise."
            )

        if display:
            display.update_stage("Classifying", "done", "Routing to Unified Loop")
            display.update_stage("Routing", "done", "Unified Prompt")
            display.update_stage("Thinking", "running")

        self.history.append({"role": "user", "content": [{"text": user_input}]})
        self.metrics["requests"] += 1

        tool_config = {"tools": TOOL_SPECS}
        loop_count = 0
        max_loops = 10

        harness.start_run(user_input)
        run_status = "ok"
        try:
            while loop_count < max_loops:
                if display:
                    display.update_stage("Thinking", "running", f"Loop {loop_count + 1}/{max_loops}")

                with harness.span("llm", "call", model=self.brain.model_id,
                                  loop=loop_count + 1) as llm_span:
                    message, stop_reason, usage = self.brain.converse(
                        self.history, system=active_system_prompt, tool_config=tool_config
                    )
                    llm_span.set(
                        stop_reason=stop_reason,
                        input_tokens=usage.get("inputTokens"),
                        output_tokens=usage.get("outputTokens"),
                        total_tokens=usage.get("totalTokens"),
                    )
                self.metrics["llm_calls"] += 1

                content = message.get("content", [])
                self.history.append({"role": "assistant", "content": content})

                tool_uses = [b["toolUse"] for b in content if "toolUse" in b]

                # No tool calls → the model is done. Its text blocks are the answer.
                if not tool_uses:
                    if display:
                        display.update_stage("Thinking", "done")
                    answer = "\n".join(b["text"] for b in content if "text" in b).strip()
                    return self._finalize(answer)

                tool_names = ", ".join(tu["name"] for tu in tool_uses)
                if display:
                    display.update_stage("Thinking", "done")
                    display.update_stage("Acting", "running", f"Tool: {tool_names}")

                # Execute every requested tool and gather one toolResult per toolUseId.
                tool_result_blocks = []
                for tu in tool_uses:
                    name = tu["name"]
                    args = tu.get("input", {}) or {}

                    with harness.span("tool", name, args=self._arg_summary(args)) as tool_span:
                        tool_result = run_tool(name, **args)
                        is_error = bool(tool_result.get("error")) or tool_result.get("success") is False
                        if is_error:
                            tool_span.set(error=tool_result.get("error") or "tool reported failure")
                            tool_span.mark_error()

                    self.metrics["tool_calls"] += 1
                    if is_error:
                        self.metrics["tool_failures"] += 1
                    else:
                        self.metrics["tool_successes"] += 1

                    # Track written files for Iron Fist
                    if name in ["write_file", "file_edit"] and tool_result.get("success"):
                        path = args.get("path")
                        if path:
                            self.written_files[path] = True
                            self.metrics["files_written"] += 1

                    tool_result_blocks.append({
                        "toolResult": {
                            "toolUseId": tu["toolUseId"],
                            "content": [{"text": json.dumps(tool_result, indent=2)}],
                            "status": "error" if is_error else "success",
                        }
                    })

                self.history.append({"role": "user", "content": tool_result_blocks})

                if display:
                    display.update_stage("Acting", "done")

                loop_count += 1

            if display:
                display.update_stage("Thinking", "done")

            return self._finalize("Max iterations reached.")
        except BaseException:
            run_status = "error"
            raise
        finally:
            harness.end_run(run_status)
            if harness.enabled and harness.persist:
                harness.save_run()

    @staticmethod
    def _arg_summary(args: dict) -> dict:
        """Compact args for the harness payload (paths/commands kept, big content trimmed)."""
        out = {}
        for k, v in args.items():
            if isinstance(v, str) and len(v) > 120:
                out[k] = f"{v[:120]}…({len(v)} chars)"
            else:
                out[k] = v
        return out

    def _finalize(self, answer: str) -> str:
        """Capture the run's files, then append an Iron Fist review of anything written."""
        if not self.written_files:
            return answer

        code_blobs = []
        captured = {}
        for path in list(self.written_files.keys()):
            result = run_tool("file_read", path=path)
            content = result.get("content", "")
            captured[path] = content
            code_blobs.append(f"# File: {path}\n{content}")

        # Retain for /test and /snippet before clearing the per-run tracker.
        self.last_run_files = captured
        self.written_files.clear()

        review = self.ironfist.review("\n\n".join(code_blobs))
        return answer + f"\n\n--- Iron Fist Review ---\n{review}"
