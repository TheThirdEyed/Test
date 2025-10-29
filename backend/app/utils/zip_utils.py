
from fastapi import UploadFile, HTTPException
import zipfile, os, io

def validate_and_extract_zip(file: UploadFile, dest: str, max_mb: int = 100):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")
    content = file.file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_mb:
        raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.1f}MB). Limit {max_mb}MB.")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            z.testzip()
            z.extractall(dest)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Corrupted or invalid ZIP file")
