import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

get_or_404_responses = {
    404: {"description": "Object not found"},
}


def get_or_404[T](obj: T | None) -> T:
    """
    Ensure that either an object was returned or an exception was raised
    """
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )
    return obj


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
