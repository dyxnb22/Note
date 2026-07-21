# 01 Python Project Template

## 项目目标

理解一个最小 Python 工程应该如何组织配置、日志和依赖。

## 你会学到什么

- `.env` 用来放本地配置和密钥
- `.gitignore` 为什么必须忽略 `.env`
- `requirements.txt` 如何记录依赖
- 为什么真实项目使用 `logging`，而不是到处 `print`

## 项目结构

```text
app/config.py   读取配置
app/logger.py   初始化日志
main.py         程序入口
```

## 如何运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## 核心代码流程

`main.py` 调用 `get_settings()` 读取配置，再调用 `setup_logger()` 创建日志对象，最后输出启动日志。

## 建议你修改的练习

- 把 `APP_NAME` 改成你自己的项目名
- 把 `LOG_LEVEL` 改成 `DEBUG`
- 增加一个 `APP_ENV=local` 配置

## 常见问题

- 找不到配置：确认已经复制 `.env.example` 为 `.env`
- 没有日志输出：确认 `LOG_LEVEL` 不是错误的字符串
