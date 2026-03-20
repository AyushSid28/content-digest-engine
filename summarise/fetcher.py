import httpx

async def fetch_url(url:str) ->str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        response=await client.get(url,headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        response.raise_for_status()
        return response.text