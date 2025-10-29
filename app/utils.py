import os, zipfile, io

ALLOWED_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".rs", ".cpp", ".c", ".cs",
    ".php", ".html", ".css", ".json", ".yml", ".yaml", ".toml", ".md", ".sql", ".env", ".ini",
    ".sh", ".bat", ".ps1", ".dockerfile", ".conf", ".cfg"
}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__"}

def is_allowed_code_file(name: str) -> bool:
    ext = os.path.splitext(name)[1].lower()
    if ext == "" and name.lower() == "dockerfile":
        return True
    return ext in ALLOWED_EXTS

def validate_and_extract_zip(zip_bytes: bytes, dest_dir: str):
    os.makedirs(dest_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            members = z.infolist()
            if not members:
                raise ValueError("Empty ZIP")
            total = 0
            code = 0
            for m in members:
                if m.is_dir(): continue
                total += 1
                parts = m.filename.split("/")
                if any(p in SKIP_DIRS for p in parts):
                    continue
                safe_path = os.path.normpath(os.path.join(dest_dir, m.filename))
                if not safe_path.startswith(os.path.abspath(dest_dir)):
                    raise ValueError("Unsafe path in archive")
                z.extract(m, dest_dir)
                if is_allowed_code_file(m.filename):
                    code += 1
            return total, code
    except zipfile.BadZipFile as e:
        raise ValueError("Corrupted ZIP") from e
