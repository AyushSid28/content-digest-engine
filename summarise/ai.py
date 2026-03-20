from typing import Generator
from .providers import create_provider, stream_with_fallback, DEFAULT_MODELS


def stream_response(
    text: str, api_key: str, model: str,
    provider_name: str = "groq", system_prompt: str | None = None,
) -> Generator[str, None, None]:
    provider = create_provider(provider_name, api_key)
    yield from provider.stream(text, model, system_prompt=system_prompt)


def stream_response_with_fallback(
    text: str, api_keys: dict, model: str | None = None,
    preferred: str | None = None, system_prompt: str | None = None,
) -> Generator[str, None, None]:
    yield from stream_with_fallback(
        text, api_keys, model=model, preferred=preferred, system_prompt=system_prompt,
    )
