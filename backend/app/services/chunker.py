
import os, re, json

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
CODE_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".sql", ".yml", ".yaml", ".toml", ".json"}

def discover_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = os.path.join(dirpath, f)
            _, ext = os.path.splitext(p)
            if ext.lower() in CODE_EXT:
                yield p

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except Exception:
        return ""

FUNC_RE = re.compile(r"^(def|async def|class|function\\s+|export\\s+function|class\\s+|const\\s+\\w+\\s*=\\s*\\([^)]*\\)\\s*=>)", re.MULTILINE)

def chunk_text(text: str, max_chars: int = 2000, overlap: int = 200):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + max_chars)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0: start = 0
    return chunks

def chunk_file(path: str):
    text = read_file(path)
    if not text.strip():
        return []
    # naive function/class boundary split for py/js/ts
    parts = re.split(FUNC_RE, text)
    if len(parts) > 1:
        # stitch back keeping markers
        segments = []
        buf = ""
        for i, part in enumerate(parts):
            if i == 0:
                buf += part
            elif part.strip() in {"def", "async def", "class", "function", "export function", "class", "const"}:
                if buf.strip():
                    segments.append(buf)
                buf = part
            else:
                buf += part
        if buf.strip():
            segments.append(buf)
        # size guard
        out = []
        for seg in segments:
            if len(seg) > 2500:
                out.extend(chunk_text(seg))
            else:
                out.append(seg)
        return out
    else:
        return chunk_text(text)
