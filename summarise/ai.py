from typing import Generator
from groq import Groq


SYSTEM_PROMPT=(

    "You are a summarising assistant.Summarise the following content."
    "Clearly,concised way in a markdown format.Use headings,bullet points"
    "and emphasis where appropriate"

)

#Streaming the response baccha
def stream_response(text:str,api_key:str,model:str)->Generator[str,None,None]:
    client=Groq(api_key=api_key)

    response=client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":text}
        ],
        stream=True,
    )
    for chunk in response:
        print(chunk.choices[0].delta.content or "",end="")