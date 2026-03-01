import trafilatura
from bs4 import BeautifulSoup

#trafilatura is used to extract content from HTML
#BeautifulSoup4 is used to clean the HTML and extract the text
def extract_content(html:str,url:str="")->str:


    text=trafilatura.extract(
        html,url=url,include_comments=False,include_tables=True,
    )

    if text and text.strip():
        return text.strip()

    soup=BeautifulSoup(html,"html.parser")
    for tag in soup(["script","style","nav","footer","header","aside"]):
      tag.decompose()


    text=soup.get_text(separator="\n",strip=True)
    if not text.strip():
        raise ValueError("Could not extract content from HTML")

    return text.strip()