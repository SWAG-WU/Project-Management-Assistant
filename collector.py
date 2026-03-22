import requests
import random
from database import add_idea, init_db
from config import GITHUB_TOKEN, GITHUB_LANGUAGES, GITHUB_TRENDING_RANGE

# 适合个人复刻的搜索关键词
REPLICABLE_KEYWORDS = [
    "tool", "cli", "automation", "productivity", "bot",
    "todo", "tracker", "dashboard", "api", "scraper",
    "utility", "helper", "manager", "monitor", "generator",
]


def collect_daily_recommendations(count=5):
    """搜寻 GitHub 上适合个人复刻的热门项目，返回推荐列表"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    keyword = random.choice(REPLICABLE_KEYWORDS)
    languages = [l.strip() for l in GITHUB_LANGUAGES if l.strip()] or ["python", "javascript"]
    lang = random.choice(languages)

    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"{keyword} language:{lang} stars:50..5000 pushed:>2025-01-01",
        "sort": "updated",
        "order": "desc",
        "per_page": 20,
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"[Collector] GitHub API error: {resp.status_code}")
            return []

        items = resp.json().get("items", [])
        # 随机挑选避免每次推荐同样的项目
        selected = random.sample(items, min(count, len(items)))
        recommendations = []
        for item in selected:
            recommendations.append({
                "name": item["name"],
                "description": (item.get("description") or "暂无描述")[:100],
                "url": item["html_url"],
                "stars": item["stargazers_count"],
                "language": item.get("language") or "N/A",
            })
        return recommendations
    except Exception as e:
        print(f"[Collector] Failed: {e}")
        return []
