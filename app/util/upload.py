import shutil
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


def get_upload_path() -> Path:
    """
    Return a Path for the upload directory
    """
    return Path(settings.UPLOAD_DIR)


def upload_file(
    file: UploadFile,
    path: str,
) -> None:
    """
    Upload a file to the provided path
    """
    p = Path(path)
    p.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with p.open("wb") as w:
        shutil.copyfileobj(file.file, w)
