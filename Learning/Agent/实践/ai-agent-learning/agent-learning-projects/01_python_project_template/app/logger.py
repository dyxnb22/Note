"""Logging setup.

真实项目不要到处 print，因为 print 很难统一控制格式、级别和输出位置。
logging 可以区分 INFO、WARNING、ERROR，也方便以后接入文件或日志平台。
"""

import logging


def setup_logger(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("project-template")
