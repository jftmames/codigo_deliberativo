import json
from datetime import datetime

class UsageMetrics:
    def __init__(self, path="usage_metrics.json"):
        self.path = path
        self.metrics = self.load_metrics()

    def load_metrics(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except:
            return {"total_sessions": 0, "total_feedback": 0, "total_nodes": 0, "session_logs": []}

    def new_session(self, root_question):
        self.metrics["total_sessions"] += 1
        self.metrics["session_logs"].append({"root": root_question, "timestamp": datetime.utcnow().isoformat()})
        self.save()

    def add_feedback(self):
        self.metrics["total_feedback"] += 1
        self.save()

    def add_nodes(self, n):
        self.metrics["total_nodes"] += n
        self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
