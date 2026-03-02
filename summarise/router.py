import sys
from pathlib import Path

#Detect if the input file isa URL,file or stdin
def detect_input_type(input:str)->str:
    if input=="-":
        return "stdin"

    if input.startswith(("http://","https://")):
        return "url"

    if Path(input).exists():
        return "file"

  


    raise ValueError(
        f"Input '{input}' is not a valid URL,file or stdin"
    )

#Detect if the input file is a PDF,text file or stdin
def detect_file_type(input:str)->str:
    suffix=Path(input).suffix.lower()
    if suffix==".pdf":
        return "pdf"

    if suffix in (".txt",".md",".markdown",".text"):
        return "text"
    return "text"


