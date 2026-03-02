import asyncio
from typing import Optional
from .config import get_api_key
from .fetcher import fetch_url
from .extractor import extract_content
from .ai import stream_response
from .output import render_markdown,console
from .router import detect_file_type,detect_input_type
from .reader import read_text_file,read_pdf,read_stdin
from .chunker import chunk_text,merge_summary


def summarise_pipeline(input:str,model:str,provider:str,output:Optional[str]=None,):
    "PIPELINE: Fetch URL-> Extract Content->Summarise->Display"
    console.print(f"Fetching: {input} ...")

    try:
        input_type=detect_input_type(input)
    except Exception as e:
        console.print(f"Error Fetching URL:")
        raise SystemExit(1)

    console.print(f"Input Type: {input_type}")

    try:
        if input_type=="url":
            console.print(f"Fetching:{input} ...")
            html=asyncio.run(fetch_url(input))
            content=extract_content(html,input)

        elif input_type=="file":
            file_type=detect_file_type(input)
            console.print(f"Reading {input} as {file_type} ")
            if file_type=="pdf":
                content=read_pdf(input)

            else:
                content=read_text_file(input)

        elif input_type=="stdin":
            console.print("reading from stdin")
            content=read_stdin()

    except Exception as e:
        console.print(f"Error Reading Input: {e}")
        raise SystemExit(1)

    api_key=get_api_key(provider)
    chunks=chunk_text(content)

    if len(chunks)==1:
        console.log(f"Summarising with {model}")
        try:
            response=stream_response(chunks[0],api_key,model)
            render_markdown(response,output)
        except Exception as e:
            console.print(f"Error during Summarisation: {e}")
            raise SystemExit(1)


    else:
        console.print(f"Large Document summarising in {len(chunks)} chunks with {model}. \n")

        try:
            partial_summaries=[]
            for i,chunk in enumerate(chunks,1):
                console.print(f"Chunk {i}/{len(chunks)} ")
                full=""
                for token in stream_response(chunk,api_key,model):
                    full+=token
                partial_summaries.append(full)


            merged=merge_summary(partial_summaries)
            console.print(f"Merging into final Summary")
            stream=stream_response(
                f"Combine these partial summary into one cohesive summary {merged}",
                api_key,model,
            )
            render_markdown(stream,output)

        except Exception as e:
            console.print(f"Error during summarisation: {e}")
            raise SystemExit(1)


