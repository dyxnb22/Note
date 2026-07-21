"""加载 .env 和环境变量"""

import sys, os

# 从项目根目录加载 .env
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")

# 尝试从父目录的 .env 加载（复用 ai-agent-learning 的配置）
parent_env = os.path.join(os.path.dirname(project_root), ".env")
if os.path.exists(parent_env):
    from dotenv import load_dotenv
    load_dotenv(parent_env)

if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

from dotenv import load_dotenv as _load
_load()
