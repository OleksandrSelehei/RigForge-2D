"""Response models for the filesystem tool."""

from pathlib import Path

from pydantic import BaseModel

from rigforge.schemas.filesystem.actions import FilesystemAction


class FilesystemResponse(BaseModel):
    """Result of a single filesystem action."""

    ok: bool
    action: FilesystemAction | None = None
    images: dict[str, Path] | None = None
    path: Path | None = None
    text: str | None = None
    data_base64: str | None = None
    error: str | None = None
