import json
import re
from datetime import date
from config import LLM_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

PLAN_PROMPT = """你是一个 vibe coding 项目规划助手。请将以下项目拆解为 {days} 天的任务计划。

项目名称：{name}
项目描述：{description}

要求：
- 每天 1~3 个子任务，工作量均衡
- 遵循 vibe coding 节奏：Day1 需求确认、Day2-3 核心功能、Day4-5 完善、Day6 测试、Day7 收尾/发布
- 输出严格的 JSON 格式，不要有任何额外说明

输出格式：
{{
  "tasks": [
    {{
      "day": 1,
      "title": "Day 1: 需求确认与环境搭建",
      "subtasks": [
        {{"id": "1-1", "content": "明确核心功能边界，写出 README 草稿", "done": false}},
        {{"id": "1-2", "content": "搭建项目目录结构，安装依赖", "done": false}}
      ]
    }}
  ]
}}"""


def _call_claude(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _call_openai(prompt: str) -> str:
    from openai import OpenAI
    kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    client = OpenAI(**kwargs)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )
    return resp.choices[0].message.content


def generate_plan(name: str, description: str, days: int = 7) -> dict:
    prompt = PLAN_PROMPT.format(name=name, description=description, days=days)

    if LLM_PROVIDER == "claude":
        raw = _call_claude(prompt)
    else:
        raw = _call_openai(prompt)

    # 提取 JSON
    match = re.search(r'\{[\s\S]*\}', raw)
    if not match:
        raise ValueError(f"LLM 返回内容无法解析为 JSON:\n{raw}")
    plan_data = json.loads(match.group())

    return {
        "project_name": name,
        "description": description,
        "start_date": str(date.today()),
        "total_days": days,
        "tasks": plan_data["tasks"],
    }
