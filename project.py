import json
from datetime import date
from config import CURRENT_PROJECT_FILE


def load_project() -> dict | None:
    if not CURRENT_PROJECT_FILE.exists():
        return None
    with open(CURRENT_PROJECT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_project(project: dict):
    with open(CURRENT_PROJECT_FILE, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)


def get_current_day_index(project: dict) -> int:
    start = date.fromisoformat(project["start_date"])
    delta = (date.today() - start).days
    return min(delta, project["total_days"] - 1)


def mark_done(task_id: str) -> bool:
    project = load_project()
    if not project:
        return False
    for day_task in project["tasks"]:
        for st in day_task["subtasks"]:
            if st["id"] == task_id:
                st["done"] = True
                save_project(project)
                return True
    return False


def get_progress(project: dict) -> tuple[int, int]:
    all_subtasks = [st for t in project["tasks"] for st in t["subtasks"]]
    done = sum(1 for st in all_subtasks if st["done"])
    return done, len(all_subtasks)
