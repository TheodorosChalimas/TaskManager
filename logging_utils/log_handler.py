import os
import json

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "todo_tasks.json")
CFG_FILE = os.path.join(LOG_DIR, "window_cfg.json")

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

class TaskManager:
    def __init__(self):
        ensure_log_dir()
        self.tasks = self.read_tasks()
        self.last_deleted = None

    def read_tasks(self):
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def save_tasks(self):
        with open(LOG_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, desc, timestamp, priority, due_date):
        self.tasks.append({
            "desc": desc,
            "timestamp": timestamp,
            "completed": False,
            "priority": priority,
            "due_date": due_date
        })
        self.save_tasks()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.last_deleted = (index, self.tasks[index])
            del self.tasks[index]
            self.save_tasks()

    def undo_delete(self):
        if self.last_deleted:
            idx, task = self.last_deleted
            self.tasks.insert(idx, task)
            self.save_tasks()
            self.last_deleted = None

    def update_task(self, index, desc=None, priority=None, due_date=None):
        if 0 <= index < len(self.tasks):
            if desc is not None:
                self.tasks[index]["desc"] = desc
            if priority is not None:
                self.tasks[index]["priority"] = priority
            if due_date is not None:
                self.tasks[index]["due_date"] = due_date
            self.save_tasks()

    def toggle_complete(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["completed"] = not self.tasks[index].get("completed", False)
            self.save_tasks()

    def set_tasks(self, tasks):
        self.tasks = tasks
        self.save_tasks()

    def save_window_cfg(self, geometry):
        with open(CFG_FILE, "w") as f:
            json.dump({"geometry": geometry}, f)

    def load_window_cfg(self):
        if not os.path.exists(CFG_FILE):
            return None
        with open(CFG_FILE, "r") as f:
            try:
                return json.load(f).get("geometry")
            except Exception:
                return None