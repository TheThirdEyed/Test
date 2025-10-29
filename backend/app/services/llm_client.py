
import os, httpx, asyncio
from typing import List, Dict, Any, Optional
from ..config import settings
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self):
        self.azure = bool(settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT)
        self.azure_endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.azure_key = settings.AZURE_OPENAI_API_KEY
        self.azure_deployment = settings.AZURE_OPENAI_DEPLOYMENT or "gpt-4o"
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL or "gpt-4o-mini"
        self.openai_embed_model = settings.OPENAI_EMBED_MODEL or "text-embedding-3-large"
        self._openai = AsyncOpenAI(api_key=self.openai_key) if self.openai_key else None

    def _ensure_available(self):
        if self.azure:
            return
        if self._openai is not None:
            return
        raise RuntimeError("No LLM provider configured. Set Azure OpenAI or OpenAI env vars.")

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        self._ensure_available()
        if self.azure:
            url = f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/chat/completions?api-version=2024-02-15-preview"
            headers = {"api-key": self.azure_key, "Content-Type": "application/json"}
            payload = {"messages": messages, "temperature": temperature}
            async with httpx.AsyncClient(timeout=90) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"]
        else:
            resp = await self._openai.chat.completions.create(  # type: ignore
                model=self.openai_model,
                messages=messages,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""

    async def embed(self, texts: List[str]) -> List[List[float]]:
        self._ensure_available()
        if self.azure:
            url = f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/embeddings?api-version=2024-02-15-preview"
            headers = {"api-key": self.azure_key, "Content-Type": "application/json"}
            payload = {"input": texts}
            async with httpx.AsyncClient(timeout=90) as client:
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                return [d["embedding"] for d in data["data"]]
        else:
            resp = await self._openai.embeddings.create(  # type: ignore
                model=self.openai_embed_model,
                input=texts,
            )
            return [item.embedding for item in resp.data]

llm_client = LLMClient()
