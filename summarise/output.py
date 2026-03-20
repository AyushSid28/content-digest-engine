import json as json_lib
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console=Console()

def render_markdown(chunks, output_path: str | None = None):
    full_text=""

    with Live(console=console,refresh_per_second=8) as live:
        for chunk in chunks:
            full_text+=chunk
            live.update(Markdown(full_text))

    console.print()
    
    if output_path:
       Path(output_path).write_text(full_text, encoding="utf-8")
       console.print(f"[dim]Saved to {output_path}[/dim]")

   
def render_json(input_source:str,input_type:str,summary:str,output_path:str | None=None):
   data={
     "input":input_source,
     "type":input_type,
     "summary":summary,
   }

   json_str=json_lib.dumps(data,indent=2,ensure_ascii=False)
   console.print(json_str)

   if output_path:
     Path(output_path).write_text(json_str,encoding="utf-8")
     console.print(f"[dim]Saved to {output_path}[/dim]")

   return data

