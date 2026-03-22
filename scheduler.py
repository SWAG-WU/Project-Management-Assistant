import time
import schedule
from datetime import date
from config import MORNING_PUSH_TIME, EVENING_PUSH_TIME
from project import load_project, get_current_day_index
from feishu import send_morning, send_evening


def _push(push_type: str):
    project = load_project()
    if not project:
        print(f"[scheduler] 无当前项目，跳过{push_type}推送")
        return
    day_index = get_current_day_index(project)
    if push_type == "morning":
        ok = send_morning(project, day_index)
    else:
        ok = send_evening(project, day_index)
    status = "成功" if ok else "失败"
    print(f"[{date.today()} {push_type}] 飞书推送{status}")


def start():
    print(f"定时推送已启动：早间 {MORNING_PUSH_TIME}，晚间 {EVENING_PUSH_TIME}")
    schedule.every().day.at(MORNING_PUSH_TIME).do(_push, "morning")
    schedule.every().day.at(EVENING_PUSH_TIME).do(_push, "evening")
    while True:
        schedule.run_pending()
        time.sleep(30)
