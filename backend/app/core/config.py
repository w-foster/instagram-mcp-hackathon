# app/core/config.py

from pydantic_settings import BaseSettings
from supabase import create_client

class Settings(BaseSettings):
    ENV: str = "local"
    MCP_URL: str = "http://localhost:8000/mcp"
    LOG_LEVEL: str = "INFO"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    @property
    def mcp_url(self):
        return self.MCP_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Create Supabase client instance here
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
