#!/usr/bin/env python3
"""
每周 Vibe Coding 提醒小助手 — CLI 入口

用法：
  python main.py new          # 新建项目，LLM 自动生成 7 天计划
  python main.py status       # 查看当前项目进度
  python main.py done <id>    # 标记子任务完成，如: done 1-2
  python main.py push morning # 手动触发早间推送
  python main.py push evening # 手动触发晚间推送
  python main.py run          # 启动定时推送守护进程
  python main.py collect      # 抓取项目灵感
  python main.py list         # 查看灵感库
"""

import sys
from project import load_project, save_project, get_current_day_index, mark_done, get_progress
from planner import generate_plan
from feishu import send_morning, send_evening


def cmd_new():
    print("=== 新建项目 ===")
    name = input("项目名称：").strip()
    if not name:
        print("项目名称不能为空")
        return
    description = input("项目描述（一两句话）：").strip()
    days_input = input("计划天数（默认 7）：").strip()
    days = int(days_input) if days_input.isdigit() else 7

    print(f"\n正在调用 LLM 生成 {days} 天任务计划，请稍候...")
    project = generate_plan(name, description, days)
    save_project(project)

    print(f"\n✅ 任务计划已生成并保存！\n")
    _print_plan(project)


def cmd_status():
    project = load_project()
    if not project:
        print("No project found, run `python main.py new` first")
        return
    day_index = get_current_day_index(project)
    done, total = get_progress(project)
    pct = int(done / total * 100) if total else 0
    bar = "#" * (pct // 10) + "-" * (10 - pct // 10)

    print(f"\n[Project] {project['project_name']}")
    print(f"   Start: {project['start_date']}  |  Day {day_index + 1}/{project['total_days']}")
    print(f"   Progress: [{bar}] {pct}%  ({done}/{total})\n")

    for i, day_task in enumerate(project["tasks"]):
        marker = ">" if i == day_index else " "
        print(f"  {marker} {day_task['title']}")
        for st in day_task["subtasks"]:
            status = "[x]" if st["done"] else "[ ]"
            print(f"      {status} [{st['id']}] {st['content']}")
    print()


def cmd_done(task_id: str):
    if not task_id:
        print("请提供任务 ID，如: python main.py done 1-2")
        return
    if mark_done(task_id):
        print(f"✅ 任务 {task_id} 已标记为完成")
    else:
        print(f"未找到任务 ID: {task_id}")


def cmd_push(push_type: str):
    project = load_project()
    if not project:
        print("暂无项目，请先运行 `python main.py new`")
        return
    day_index = get_current_day_index(project)
    if push_type == "morning":
        ok = send_morning(project, day_index)
    elif push_type == "evening":
        ok = send_evening(project, day_index)
    else:
        print("push 类型须为 morning 或 evening")
        return
    print("推送成功" if ok else "推送失败，请检查 FEISHU_WEBHOOK_URL 配置")


def cmd_run():
    from scheduler import start
    start()


def cmd_collect():
    from collector import collect_github_trending
    from database import init_db
    print("=== Collecting project ideas ===")
    init_db()
    count = collect_github_trending()
    print(f"\n[Done] Collected {count} new projects")


def cmd_list():
    from database import init_db, list_ideas
    init_db()
    ideas = list_ideas(limit=20)
    if not ideas:
        print("No ideas yet, run `python main.py collect` to start")
        return
    print(f"\n=== Ideas Library (Latest {len(ideas)}) ===\n")
    for row in ideas:
        print(f"[{row[0]}] {row[1]}")
        desc = row[2] if row[2] else ""
        desc_clean = desc.encode('ascii', 'ignore').decode('ascii')
        print(f"    {desc_clean[:80]}...")
        print(f"    Tags: {row[4]}  |  URL: {row[3]}\n")


def _print_plan(project: dict):
    print(f"📌 {project['project_name']}  ({project['total_days']} 天)\n")
    for day_task in project["tasks"]:
        print(f"  {day_task['title']}")
        for st in day_task["subtasks"]:
            print(f"    ⬜ [{st['id']}] {st['content']}")
    print()


def main():
    args = sys.argv[1:]
    if not args or args[0] == "help":
        print(__doc__)
        return

    cmd = args[0]
    if cmd == "new":
        cmd_new()
    elif cmd == "status":
        cmd_status()
    elif cmd == "done":
        cmd_done(args[1] if len(args) > 1 else "")
    elif cmd == "push":
        cmd_push(args[1] if len(args) > 1 else "")
    elif cmd == "run":
        cmd_run()
    elif cmd == "collect":
        cmd_collect()
    elif cmd == "list":
        cmd_list()
    else:
        print(f"未知命令: {cmd}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
