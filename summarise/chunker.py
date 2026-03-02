def chunk_text(text:str,max_chars:int=24000)->list[str]:
    """Split text into chunks"""
    if len(text)<=max_chars:
        return [text]

    chunks=[]
    paragraphs=text.split("\n\n")
    current=""
    for para in paragraphs:
        if len(current)+len(para)+1>max_chars:
            if current:
                chunks.append(current.strip())
            current=para
        else:
            current=current.strip() + "\n\n" + para

    if current.strip():
        chunks.append(current.strip())

    return chunks

def merge_summary(summaries:list[str])->str:
    """Combine multiple chunk summaries into a sinle summary"""
    return "\n\n---\n\n".join(summaries)
