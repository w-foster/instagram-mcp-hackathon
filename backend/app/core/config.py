# app/core/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "local")  # 'local' or 'prod'
    MCP_LOCAL_URL: str = "http://localhost:8001"
    MCP_PROD_URL: str = "https://mcp.yourdomain.com/api"
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def mcp_url(self):
        return self.MCP_LOCAL_URL if self.ENV == "local" else self.MCP_PROD_URL

settings = Settings()
