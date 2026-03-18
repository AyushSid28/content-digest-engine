from typing import Generator
from .providers import create_provider, stream_with_fallback, DEFAULT_MODELS


def stream_response(text: str, api_key: str, model: str, provider_name: str = "groq") -> Generator[str, None, None]:
    provider = create_provider(provider_name, api_key)
    yield from provider.stream(text, model)



def stream_response_with_fallback(
 text: str, api_keys: dict, model: str | None = None,
    preferred: str | None = None,
) -> Generator[str, None, None]:
    """Stream with automatic fallback across providers."""
    yield from stream_with_fallback(text, api_keys, model=model, preferred=preferred)