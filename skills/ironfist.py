from core.brain import Brain

class IronFist:
    def __init__(self, brain: Brain):
        self.brain = brain
        
    def review(self, final_response: str) -> str:
        prompt = f"Review this code. Score Correctness, Performance, Readability out of 10. List issues and improvements. Be brutal. CODE: {final_response}"
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        system_prompt = "You are Iron Fist — an optimization and review specialist. You are precise and quality-focused. Review for correctness, performance, readability."
        
        return self.brain.think(messages, system=system_prompt)
