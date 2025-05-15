import json
from datetime import datetime

class ReasoningTracker:
    def __init__(self, root_question):
        self.log = {
            "root": root_question,
            "inquiry": None,
            "responses": {},
            "focus": [],
            "times": [],
            "steps": []  # Para registrar cada acción deliberativa
        }

    def log_inquiry(self, tree):
        self.log["inquiry"] = tree
        self._stamp("inquiry")

    def log_responses(self, resp):
        self.log["responses"] = resp
        self._stamp("responses")

    def log_focus_change(self, s):
        self.log["focus"].append(s)
        self._stamp("focus")

    def log_event(self, event_type, content, marco=None, parent_node=None):
        self.log["steps"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "content": content,
            "marco": marco,
            "parent_node": parent_node
        })

    def _stamp(self, evt):
        self.log["times"].append({evt: datetime.utcnow().isoformat()})

    def export(self):
        return json.dumps(self.log, ensure_ascii=False, indent=2)
