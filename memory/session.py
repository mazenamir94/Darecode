import os
import json
from datetime import datetime

class SessionManager:
    def __init__(self, agent):
        self.agent = agent
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def _generate_name(self) -> str:
        if not self.agent.history:
            return "empty_session"
            
        first_messages = self.agent.history[:6]  # first 3 exchanges
        summary = "\n".join([f"{m['role']}: {m['content'][0]['text'][:100]}" for m in first_messages])
        
        result = self.agent.brain.think(
            [{"role": "user", "content": [{"text": f"Give this conversation a short 3-5 word title. Reply with ONLY the title, nothing else.\n\n{summary}"}]}],
            system="You are a title generator. Reply with only a short title."
        )
        
        # Clean title
        clean = result.strip().replace(" ", "_").replace("/", "-").lower()
        # Keep alphanumeric, underscores, hyphens
        clean = "".join(c for c in clean if c.isalnum() or c in ("_", "-"))
        return clean[:50]
        
    def save(self) -> str:
        if len(self.agent.history) <= 2:
            return ""
            
        if hasattr(self, 'loaded_path') and self.loaded_path:
            filepath = self.loaded_path
        else:
            title = self._generate_name()
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"{timestamp}_{title}.json"
            filepath = os.path.join(self.sessions_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.agent.history, f, indent=2)
            
        self.loaded_path = filepath
        return filepath
        
    def get_sessions(self) -> list:
        sessions = []
        if not os.path.exists(self.sessions_dir):
            return sessions
            
        for f in os.listdir(self.sessions_dir):
            if f.endswith(".json"):
                path = os.path.join(self.sessions_dir, f)
                # Parse timestamp and title from filename
                parts = f[:-5].split("_", 1)
                date_str = parts[0]
                title = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
                
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    display_date = date_obj.strftime("%b %d, %Y")
                except ValueError:
                    display_date = date_str
                    
                sessions.append({
                    "path": path,
                    "title": title,
                    "date": display_date,
                    "raw_date": date_str
                })
                
        # Sort by raw date descending
        sessions.sort(key=lambda x: x["raw_date"], reverse=True)
        return sessions
        
    def load(self, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.agent.history = json.load(f)
            self.loaded_path = path
            return True
        return False
