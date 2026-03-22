import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")
MORNING_PUSH_TIME = os.getenv("MORNING_PUSH_TIME", "09:00")
EVENING_PUSH_TIME = os.getenv("EVENING_PUSH_TIME", "21:00")

CURRENT_PROJECT_FILE = DATA_DIR / "current_project.json"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
COLLECT_SOURCES = os.getenv("COLLECT_SOURCES", "github").split(",")
GITHUB_LANGUAGES = os.getenv("GITHUB_LANGUAGES", "").split(",")
GITHUB_TRENDING_RANGE = os.getenv("GITHUB_TRENDING_RANGE", "weekly")
IDEAS_DB_FILE = DATA_DIR / "ideas.db"
