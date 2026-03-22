import requests
from database import add_idea, init_db
from config import GITHUB_TOKEN, GITHUB_LANGUAGES, GITHUB_TRENDING_RANGE

def collect_github_trending():
    """抓取 GitHub Trending 项目"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    collected = 0

    for lang in GITHUB_LANGUAGES:
        lang = lang.strip()
        if not lang:
            continue

        url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"language:{lang} stars:>50",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
            if resp.status_code != 200:
                print(f"GitHub API error ({lang}): {resp.status_code}")
                continue

            data = resp.json()
            for item in data.get("items", []):
                title = item["name"]
                description = item.get("description", "")[:200]
                source_url = item["html_url"]
                tags = f"{lang},github"

                if add_idea(title, description, source_url, tags):
                    collected += 1
                    print(f"[OK] {title}")

        except Exception as e:
            print(f"Failed ({lang}): {e}")

    return collected
