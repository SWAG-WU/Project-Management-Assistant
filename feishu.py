import requests
from datetime import date, timedelta
from config import FEISHU_WEBHOOK_URL

MOTIVATIONS = [
    "今天也是充满可能的一天，加油！",
    "一步一步来，每天进步一点点。",
    "代码写起来，灵感自然来。",
    "专注当下，完成比完美更重要。",
    "Vibe coding，享受过程！",
]


CREATE_WORKFLOW_URL = "https://github.com/SWAG-WU/Project-Management-Assistant/actions/workflows/create-project.yml"


def _post(card: dict) -> bool:
    if not FEISHU_WEBHOOK_URL:
        print("[飞书] 未配置 FEISHU_WEBHOOK_URL，跳过推送")
        return False
    resp = requests.post(FEISHU_WEBHOOK_URL, json={"msg_type": "interactive", "card": card}, timeout=10)
    ok = resp.status_code == 200 and resp.json().get("code") == 0
    if not ok:
        print(f"[飞书] 推送失败: {resp.text}")
    return ok


def _md_element(content: str) -> dict:
    return {"tag": "div", "text": {"tag": "lark_md", "content": content}}


def _divider() -> dict:
    return {"tag": "hr"}


def send_morning(project: dict, day_index: int, recommendations: list = None):
    """早间推送：今日任务 + 项目推荐"""
    total = project["total_days"]
    day_num = day_index + 1
    day_tasks = project["tasks"][day_index] if day_index < len(project["tasks"]) else None

    import random
    motivation = random.choice(MOTIVATIONS)

    desc = project.get("description", "")
    lines = [f"**📋 今日任务 · Day {day_num}/{total}**\n"]
    if desc:
        lines.append(f"**项目简介：** {desc}\n")
    if day_tasks:
        lines.append(f"**{day_tasks['title']}**\n")
        for st in day_tasks["subtasks"]:
            status = "✅" if st["done"] else "⬜"
            lines.append(f"{status} {st['content']}")
    lines.append(f"\n_{motivation}_")

    elements = [_md_element("\n".join(lines))]

    # 项目推荐板块
    if recommendations:
        elements.append(_divider())
        rec_lines = ["**🔍 今日开源项目推荐**\n"]
        for i, rec in enumerate(recommendations, 1):
            rec_lines.append(f"**{i}. [{rec['name']}]({rec['url']})**")
            rec_lines.append(f"   ⭐ {rec['stars']}  |  🔤 {rec['language']}")
            rec_lines.append(f"   {rec['description']}\n")
        elements.append(_md_element("\n".join(rec_lines)))
        elements.append(_divider())
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "🚀 复刻项目（点击创建计划）"},
                "type": "primary",
                "url": CREATE_WORKFLOW_URL,
            }],
        })

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"🌅 早安！{project['project_name']}"},
            "template": "blue",
        },
        "elements": elements,
    }
    return _post(card)


def send_evening(project: dict, day_index: int):
    """晚间推送：进度回顾"""
    total = project["total_days"]
    day_num = day_index + 1
    day_tasks = project["tasks"][day_index] if day_index < len(project["tasks"]) else None

    # 计算整体进度
    all_subtasks = [st for t in project["tasks"] for st in t["subtasks"]]
    done_count = sum(1 for st in all_subtasks if st["done"])
    total_count = len(all_subtasks)
    pct = int(done_count / total_count * 100) if total_count else 0
    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)

    desc = project.get("description", "")
    lines = [f"**📊 进度回顾 · Day {day_num}/{total}**\n"]
    if desc:
        lines.append(f"**项目简介：** {desc}\n")

    if day_tasks:
        lines.append("**今日任务完成情况：**")
        for st in day_tasks["subtasks"]:
            status = "✅ 已完成" if st["done"] else "❌ 未完成"
            lines.append(f"- {st['content']}  {status}")

    lines.append(f"\n**整体进度：** {bar} {pct}%  ({done_count}/{total_count})")

    # 明日预告
    next_idx = day_index + 1
    if next_idx < len(project["tasks"]):
        next_day = project["tasks"][next_idx]
        lines.append(f"\n**明日预告：** {next_day['title']}")
        for st in next_day["subtasks"]:
            lines.append(f"  · {st['content']}")
    else:
        lines.append("\n🎉 **项目已进入最后阶段，加油冲刺！**")

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"🌙 晚间复盘 · {project['project_name']}"},
            "template": "green" if pct >= 50 else "orange",
        },
        "elements": [_md_element("\n".join(lines))],
    }
    return _post(card)
