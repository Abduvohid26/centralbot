from urllib.parse import urlparse

async def extract_platform_from_link(link: str) -> str:
    parsed = urlparse(link)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    platform = domain.split('.')[0]
    return platform