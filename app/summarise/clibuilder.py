"""
This module is used for builder the CLI with automatic help generation ,type hints, and error correction
"""

import typer


def main(
    model:str= typer.Option(...,help="The model to use for summarisation"),
    provider:str= typer.Option(...,help="The provider to use for summarisation"),
    output:str= typer.Option(...,help="The output to use for summarisation"),
):
 


typer.echo(f"Summarising with {model} from {provider} and outputting to {output}")

if __name__ == "__main__":
    main()