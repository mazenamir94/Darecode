from core.agent import Agent

import sys

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', 'replace').decode('cp1252', 'replace'))

def test():
    agent = Agent()
    
    safe_print("\n--- Test 1: Backend ---")
    agent.reset()
    res1 = agent.run("create a postgres schema for users")
    
    safe_print("\n--- Test 2: Web ---")
    agent.reset()
    res2 = agent.run("build a react component for a login form")
    
    safe_print("\n--- Test 3: Debug ---")
    agent.reset()
    res3 = agent.run("traceback in main.py, fix the bug")

if __name__ == "__main__":
    test()
