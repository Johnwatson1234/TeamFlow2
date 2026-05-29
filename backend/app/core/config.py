import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BASE_DIR / ".env")
_load_env_file(BASE_DIR / ".env.local")


DATABASE_URL = f"sqlite:///{DATA_DIR / 'teamflow.db'}"
SECRET_KEY = "teamflow-demo-secret-key-for-course-project-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
LLM_API_KEY = (
    os.getenv("TEAMFLOW_LLM_API_KEY")
    or os.getenv("BIGMODEL_API_KEY")
    or ""
).strip()
LLM_BASE_URL = (
    os.getenv("TEAMFLOW_LLM_BASE_URL")
    or os.getenv("BIGMODEL_BASE_URL")
    or "https://open.bigmodel.cn/api/paas/v4"
).strip()
LLM_MODEL = (
    os.getenv("TEAMFLOW_LLM_MODEL")
    or os.getenv("BIGMODEL_MODEL")
    or "glm-4.7-flash"
).strip()
LLM_TIMEOUT_SECONDS = float(os.getenv("TEAMFLOW_LLM_TIMEOUT_SECONDS", "20"))
