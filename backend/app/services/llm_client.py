# app/services/llm_client.py

import os
import httpx
from app.core.config import settings

class LLMClient:
    def __init__(self, api_key: str = settings.LLM_API_KEY):
        self.api_key = api_key
        self.endpoint = "https://api.openai.com/v1/chat/completions"  # example

    async def ask(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.endpoint, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
