from core.tools import run_tool

# 1. bash
print("=== BASH ===")
print(run_tool("bash", command="echo hello from darecode"))

# 2. glob — finds all python files in current dir
print("\n=== GLOB ===")
print(run_tool("glob", pattern="**/*.py", base_dir="."))

# 3. file_read — reads this file itself
print("\n=== FILE_READ ===")
result = run_tool("file_read", path="core/tools.py")
print(f"Lines: {result['lines']}, First 100 chars: {result['content'][:100]}")

# 4. grep — finds 'def' in tools.py
print("\n=== GREP ===")
print(run_tool("grep", pattern="def ", path="core/tools.py"))

# 5. write_file — writes a test file
print("\n=== WRITE_FILE ===")
print(run_tool("write_file", path="workspace/test_output.txt", content="DareCode wrote this.\n"))
