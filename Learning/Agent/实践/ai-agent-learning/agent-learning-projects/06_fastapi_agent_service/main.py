import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent_service import run_agent
from app.config import Settings


settings = Settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("fastapi-agent")

app = FastAPI(title=settings.app_name)


class ChatRequest(BaseModel):
    # Pydantic 负责校验请求结构。后端 API 不能假设客户端永远传对数据。
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """把 Agent 包装成 HTTP API。

    CLI 程序适合自己学习；API 服务适合被前端、其他服务或自动化系统调用。
    """
    try:
        answer = run_agent(request.message)
        return ChatResponse(answer=answer)
    except Exception as exc:
        logger.exception("agent failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
