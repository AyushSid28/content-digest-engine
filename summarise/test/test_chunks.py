import os
import pytest
from unittest.mock import patch
from summarise.config import get_api_key, get_all_api_keys

@patch.dict(os.environ, {"GROQ_API_KEY": "test-key-123"})
def test_get_api_key_groq():
    key = get_api_key("groq")
    assert key == "test-key-123"

def test_get_api_key_unknown():
    with pytest.raises(SystemExit):
        get_api_key("unknown_provider")

@patch.dict(os.environ, {}, clear=True)
def test_get_api_key_missing():
    with pytest.raises(SystemExit):
        get_api_key("groq")

@patch.dict(os.environ, {"GROQ_API_KEY": "g-key", "OPENAI_API_KEY": "o-key"}, clear=True)
def test_get_all_api_keys():
    keys = get_all_api_keys()
    assert keys["groq"] == "g-key"
    assert keys["openai"] == "o-key"
    assert "openrouter" not in keys

@patch.dict(os.environ, {}, clear=True)
def test_get_all_api_keys_empty():
    keys = get_all_api_keys()
    assert keys == {}