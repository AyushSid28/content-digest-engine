import typer
from typing import Optional

app=typer.Typer(help="Summarise AI powered content summarisation CLI")

@app.command()
def main(
    input:str= typer.Argument(...,help="URL to summarise"),
    model:str= typer.Option("llama-3.3-70b-versatile","--model","-m",help="Model to use for summarisation",),
    provider:str= typer.Option("groq","--provider","-p",help="AI Provider"),

    output: Optional[str]=typer.Option(None,"--output","-o",help="Save summary to file instead of only printing",),

    timestamps: bool = typer.Option(False,"--timestamps","-t",help="Input timestamps in Youtube summaries"),

    json_mode:bool=typer.Option(False,"--json","-j",help="output structured JSON instead of Markdown"),

    theme:str=typer.Option(
        "default","--theme",help="Output theme: default,minimal,detailed,bullet-points",
    ),


):
    """Summarise URL,file or Piped using AI"""
    from .core import summarise_pipeline
    summarise_pipeline(input=input,model=model,provider=provider,output=output,timestamps=timestamps,json_mode=json_mode,theme=theme,)