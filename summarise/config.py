import os

def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

KEY_MAP={
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY", 
    "openrouter": "OPENROUTER_API_KEY",
}


def get_api_key(provider:str):
    load_env()
  
    env_var=KEY_MAP.get(provider)
    if not env_var:
        raise SystemExit(f"Unknown provider: '{provider}'")

    key=os.getenv(env_var)
    if not key:
        raise SystemExit(
            f"API key not found. Set {env_var} in your .env file or environment."
        )
    return key 


def get_all_api_keys()->dict:
    """Return all available api keys"""
    load_env()
    keys={}
    for provider,env_var in KEY_MAP.items():
        key=os.getenv(env_var)
        if key:
            keys[provider]=key
    return keys