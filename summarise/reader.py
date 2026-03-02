import sys
from pathlib import Path

#Read plain text or markdown file
def read_text_file(path:str)->str:
   content=Path(path).read_text(encoding="utf-8")
   if not content.strip():
      raise ValueError(f"File is empty: {path}")
   return content.strip()


#Extract text from PDF 
def read_pdf(path:str)->str:
    try:
        import pdfplumber
        text=""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
               page_text = page.extract_text()
               if page_text:
                   text += page_text + "\n"


        if text.strip():
            return text.strip()

    except Exception:
        pass

    from PyPDF2 import PdfReader
    reader=PdfReader(path)
    text=""
    for page in reader.pages:
        page_text=page.extract_text()
        if page_text:
            text+=page_text + "\n"
        
    if not text.strip():
        raise ValueError(f"Could not extract text from PDF: {path}")
    return text.strip()


def read_stdin()->str:
    if sys.stdin.isatty():
        raise ValueError("No piped input detected. Use echo 'text' | summarise -")
    content=sys.stdin.read()
    if not content.strip():
        raise ValueError("piped out is empty")
    return content.strip()



