from typing import Generator
from abc import ABC,abstractmethod


SYSTEM_PROMPT=(
    "You are a summarisation assistant.Summarise the following content."
    "clearly,concisely in markdown format.Use headings and bullet points"
    "and emphasis where appropriate."
)

DEFAULT_PROVIDER={
    "groq":"llama-3.3-70b-versatile",
    "openai":"gpt-4o-mini",
    "openrouter":"meta-llama/llama-3.3-70b-infrastruct:free",
}


class Provider(ABC):
    @abstractmethod
    def stream(self,text:str,model:str)->Generator[str,None,None]:
        ...

    @abstractmethod
    def name(self)->str:
        ...


class GroqProvider(Provider):
    def __init__(self,api_key:str):
        from groq import Groq
        self.client=Groq(api_key=api_key)

    def name(self)->str:
        return "groq"

    def stream(self,text:str,model:str)->Generator[str,None,None]:
        response=self.client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text},
            ],
            stream=True,
        )
        for chunk in response:
            delta=chunk.choices[0].delta.content
            if delta:
                yield delta



class OpenAIProvider(Provider):
    def __init__(self,api_key:str):
        from openai import OpenAI
        self.client=OpenAI(api_key=api_key)



    def name(self)->str:
        return "openai"

    def stream(self,text:str,model:str)->Generator[str,None,None]:
        response=self.client.chat.completiions.create(
            model=model,
            message=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text},

            ],
            stream=True,
        )
        for chunk in response:
            delta=chunk.choices[0].delta.content
            if delta:
                yield delta

    
class OpenRouterProvider(Provider):
    def __init__(self,api_key:str):
        from openai import OpenAI
        self.client=OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    

    def name(self)->str:
        return "openrouter"

    def stream(self,text:str,model:str)->Generator[str,None,None]:
        response=self.client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text},
            ],
            stream=True,
        )
        for chunk in response:
            delta=chunk.choices[0].delta.content
            if delta:
                yield delta

PROVIDER_CLASSES={
    "groq":GroqProvider,
    "openai":OpenAIProvider,
    "openrouter":OpenRouterProvider,
}

def get_provider(provider:str)->Provider:
    """Create a provider instance by name."""
    cls=PROVIDER_CLASSES.get(provider)
    if not cls:
        raise ValueError(f"unknown provider: `{name}`")

    return cls(api_key=api_key)


def auto_select_provider(api_key:str)->str:
    if provider_name=="groq":
        return "llama-3.3-70b-versatile"
    elif provider_name=="openai":
        if content_length>50000:
            return "gpt-4o"
        return "gpt-4o-mini"
    elif provider_name="openrouter:
        return "meta-llama/llama-3.3-70b-instruct:free"
    return DEFAULT_MODELS.get(provider_name,"llama-3.3-70b-versatile")


def stream_with_fallback(
    text:str,api_key:dict,model:str |None=None, preferred:str | None=None,
)-> Generator[str,None,None]:
   """Try providers in order: preferred → groq → openrouter → openai.
    Yields chunks from the first provider that succeeds.
    """
   chain=_build_chain(preferred,api_keys)

   last_error=None
   for provider in chain:
     key=api_keys.get(provider_name)
     if not key:
        continue
     use_model=model or auto_select_model(provider_model,len(text))
     try: 
        provider=create_provider(provider,key)
        chunks=list(provider.stream(text,use_model))
        yield chunks from chunks
        return
     except Exception as e:
        last_error=e
        continue

   raise RuntimeError(
        f"All providers failed: {last_error}"
    )

def _build_chain(preferred:str | None,api_keys;dict)->list[str]:
    """Build the fallback chain order"""
    default_order=["groq","openrouter","openai"]
    if preferred and preferred in api_keys:
        default_order.remove(preferred)
        default_order.insert(0,preferred)
    return default_order

