import typer
from typing import Optional

app=typer.Typer(help="Summarise AI powered content summarisation CLI")

@app.command()
def main(
    input:str= typer.Argument(...,help="URL to summarise"),
    model:str= typer.Option("llama-3.3-70b-versatile","--model","-m",help="Model to use for summarisation",),
    provider:str= typer.Option("groq","--provider","-p",help="AI Provider"),

    output: Optional[str]=typer.Option(None,"--output","-o",help="Save summary to file instead of only printing",),


):
    """Summarise URL,file or Piped using AI"""
    from .core import summarise_pipeline
    summarise_pipeline(input=input,model=model,provider=provider,output=output)