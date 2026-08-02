"""Configuration loading.

真实项目通常会有不同环境：本地、测试、生产。
.env 文件让我们不用把配置写死在代码里，也避免把密码、Token 提交到 Git。
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# 从项目根目录加载本地配置；生产环境应改用密钥管理服务注入变量。
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str
    log_level: str


def get_settings() -> Settings:
    # 默认值让示例在没有 .env 时仍可启动，但不能替代正式配置校验。
    return Settings(
        app_name=os.getenv("APP_NAME", "Agent Learning Template"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
