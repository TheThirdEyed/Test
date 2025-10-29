
import httpx, re
from typing import List, Tuple

ALLOWLIST = [
    "https://fastapi.tiangolo.com",
    "https://docs.pydantic.dev",
    "https://www.sqlalchemy.org",
    "https://owasp.org",
    "https://docs.sqlalchemy.org",
    "https://react.dev",
    "https://beta.reactjs.org",
]

async def fetch_allowlisted(urls: List[str]) -> List[Tuple[str, str]]:
    out = []
    async with httpx.AsyncClient(timeout=15) as client:
        for u in urls:
            if not any(u.startswith(a) for a in ALLOWLIST):
                continue
            try:
                r = await client.get(u)
                r.raise_for_status()
                text = re.sub(r"\\s+", " ", r.text)
                out.append((u, text[:2000]))
            except Exception:
                pass
    return out
