import asyncio
import time
from typing import Optional, Dict, Any, Callable, Awaitable, TypeVar
from target.base import BaseTarget, TargetResponse
from google import genai
from google.genai import types
import openai

T = TypeVar("T")


async def _call_with_retry(
    fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> T:

    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            last_exc = e
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
    raise last_exc 


class GeminiTarget(BaseTarget):
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.client = genai.Client(api_key=api_key)

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **generation_kwargs
    ) -> TargetResponse:
        start = time.perf_counter()

        config_dict = {**self.config, **generation_kwargs}
        if system_prompt:
            config_dict["system_instruction"] = system_prompt

        config = types.GenerateContentConfig(**config_dict)

        response = await _call_with_retry(
            lambda: self.client.aio.models.generate_content(
                model=self.model_name, contents=prompt, config=config
            )
        )

        latency = (time.perf_counter() - start) * 1000

        usage = None
        if response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
            }

        raw = None
        try:
            raw = response.to_dict()
        except Exception:
            pass

        return TargetResponse(
            text=response.text or "",
            model=self.model_name,
            usage=usage,
            latency_ms=latency,
            raw=raw,
        )


class OpenAICompatibleTarget(BaseTarget):
    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model_name, **kwargs)
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **generation_kwargs
    ) -> TargetResponse:
        start = time.perf_counter()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await _call_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **{**self.config, **generation_kwargs},
            )
        )

        latency = (time.perf_counter() - start) * 1000

        usage = None
        if response.usage:
            usage = response.usage.model_dump()

        return TargetResponse(
            text=response.choices[0].message.content or "",
            model=self.model_name,
            usage=usage,
            latency_ms=latency,
            raw=response.model_dump(),
        )
