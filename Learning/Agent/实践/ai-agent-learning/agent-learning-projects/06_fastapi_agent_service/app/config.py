import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# 配置文件相对项目根目录定位，避免从不同工作目录启动时读取错 .env。
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    # 默认值只适合本地学习；生产配置应来自受控环境或 Secret 系统。
    app_name: str = os.getenv("APP_NAME", "FastAPI Agent Service")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
