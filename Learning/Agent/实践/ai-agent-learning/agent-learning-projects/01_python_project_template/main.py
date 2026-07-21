from app.config import get_settings
from app.logger import setup_logger


def main() -> None:
    settings = get_settings()
    logger = setup_logger(settings.log_level)

    # requirements.txt 记录项目依赖，别人拿到项目后才能稳定安装同一组包。
    logger.info("Application started: %s", settings.app_name)


if __name__ == "__main__":
    main()
