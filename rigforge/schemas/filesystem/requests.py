"""Request models for the filesystem tool."""

from typing import Literal

from pydantic import BaseModel

from rigforge.schemas.filesystem.actions import FilesystemAction


class FilesystemRequest(BaseModel):
    """Arguments for one filesystem action."""

    action: FilesystemAction
    path: str | None = None
    content: str = ""
    content_encoding: Literal["utf-8", "base64"] = "utf-8"
    overwrite: bool = False
    recursive: bool = False
