from pathlib import Path
from .cache import get_cached_transcription,save_transcription


AUDIO_EXTENSIONS={".mp3",".wav",".m4a",".ogg"}

def is_audio_file(path:str)->bool:
    return Path(path).suffix.lower() in AUDIO_EXTENSIONS

def transcribe(filepath:str,api_key:str |None = None, use_groq:bool=True)->str:
   """Transcribe audio.checks cache first,then GROQ API,then local whisper"""

   cached=get_cached_transcription(filepath)
   if cached:
    return cached

   if use_groq and api_key:
    text=_transcribe_groq(filepath,api_key)
   else:
    text=_transcribe_local(filepath)

   save_transcription(filepath,text)

   return text

def _transcribe_groq(filepath:str,api_key:str)->str:
    """Transcribe using local openai-whisper"""
    from groq import Groq
    client=Groq(api_key=api_key)
    with open(filepath,"rb") as f:
        result=client.audio.transcriptions.create(
            file=(Path(filepath).name,f.read()),

            model="whisper-large-v3",
        )
    return result.text


def _transcribe_local(filepath:str)->str:
    """Transcribe using local whisper:"""
    try:
        import whisper
    except ImportError:
        raise RuntimeError(
            "Local Whisper not installed."
        )
    model=whisper.load_model("base")
    result=model.transcribe(filepath)
    return result["text"]



