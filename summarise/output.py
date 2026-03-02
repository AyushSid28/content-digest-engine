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

   