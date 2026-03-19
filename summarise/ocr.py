from pathlib import Path

IMAGE_EXTENSIONS={".png",".jpg",".jpeg",".webp",".tiff",".tif",".bmp",".gif"}

def is_image_file(path:str)->bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS

def extract_image_text(path:str)->str:
    """Extract text from an image using pytesseract + Pillow"""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise RuntimeError(
            "OCR dependencies not installed. Run: pip install pillow pytesseract\n"
            "Also install Tesseract: brew install tesseract (macOS)"
        )

    image=Image.open(path)
    text=pytesseract.image_to_string(image)
    if not text.strip():
        return ""
    return text.strip()


def describe_image_vision(image_path:str,api_key:str,provider_name:str="openai")->str:
    """Use a vision-capable model to describe/summarise an image"""
    import base64

    with open(image_path,"rb") as image_file:
        b64=base64.b64encode(image_file.read()).decode("utf-8")

    suffix=Path(image_path).suffix.lower().lstrip(".")
    mime_map={"jpg":"jpeg","tif":"tiff"}
    mime=mime_map.get(suffix,suffix)

    if provider_name=="openai":
        from openai import OpenAI
        client=OpenAI(api_key=api_key)
        response=client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role":"user",
                "content":[
                    {"type":"text","text":"Describe and summarise the content of this image in detail."},
                    {"type":"image_url","image_url":{"url":f"data:image/{mime};base64,{b64}"}},
                ],
            }],
        )
        return response.choices[0].message.content

    raise ValueError(f"Vision not supported for provider: {provider_name}")


def process_image(image_path:str,api_key:str | None=None,vision_provider:str | None=None)->str:
    """Process an image: try OCR first, fall back to Vision API if OCR yields little text."""

    ocr_text=extract_image_text(image_path)

    if len(ocr_text)>50:
        return f"[OCR extracted text from: {Path(image_path).name}]\n\n{ocr_text}"

    if api_key and vision_provider:
        vision_text=describe_image_vision(image_path,api_key,vision_provider)
        return f"[Vision API description of: {Path(image_path).name}]\n\n{vision_text}"

    if ocr_text:
        return f"[OCR extracted text from: {Path(image_path).name}]\n\n{ocr_text}"

    raise ValueError(
        f"Could not extract text from image: {image_path}\n"
        "Set OPENAI_API_KEY for Vision API fallback."
    )
