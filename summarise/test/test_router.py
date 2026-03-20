import pytest
from unittest.mock import patch
from summarise.router import detect_input_type, detect_file_type

def test_stdin():
    assert detect_input_type("-") == "stdin"

def test_url():
    assert detect_input_type("https://example.com/article") == "url"
    assert detect_input_type("http://example.com") == "url"

def test_youtube():
    assert detect_input_type("https://www.youtube.com/watch?v=abc123") == "youtube"
    assert detect_input_type("https://youtu.be/abc123") == "youtube"

def test_github():
    assert detect_input_type("https://github.com/owner/repo") == "github"

@patch("summarise.router.Path.exists", return_value=True)
@patch("summarise.router.is_audio_file", return_value=False)
@patch("summarise.router.is_image_file", return_value=False)
def test_file(mock_img, mock_audio, mock_exists):
    assert detect_input_type("/some/file.txt") == "file"

@patch("summarise.router.Path.exists", return_value=True)
@patch("summarise.router.is_audio_file", return_value=True)
def test_audio_file(mock_audio, mock_exists):
    assert detect_input_type("/some/file.mp3") == "audio"

@patch("summarise.router.Path.exists", return_value=True)
@patch("summarise.router.is_audio_file", return_value=False)
@patch("summarise.router.is_image_file", return_value=True)
def test_image_file(mock_img, mock_audio, mock_exists):
    assert detect_input_type("/some/file.png") == "image"

def test_invalid():
    with pytest.raises(ValueError):
        detect_input_type("/nonexistent/file.xyz")

def test_detect_file_type():
    assert detect_file_type("doc.pdf") == "pdf"
    assert detect_file_type("notes.md") == "text"
    assert detect_file_type("readme.txt") == "text"
    assert detect_file_type("data.csv") == "text"