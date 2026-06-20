import io, httpx, trafilatura
from pypdf import PdfReader

def from_pdf(buf: bytes) -> str:
    reader = PdfReader(io.BytesIO(buf))
    return "\n".join((p.extract_text() or "") for p in reader.pages)

def from_url(url: str) -> str:
    r = httpx.get(url, follow_redirects=True, timeout=20,
                  headers={"User-Agent": "Mozilla/5.0"})
    return trafilatura.extract(r.text) or ""