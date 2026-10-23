"""Shared filesystem tool infrastructure."""

import os
from pathlib import Path


class FilesystemToolError(Exception):
    """Base error raised by filesystem tools."""


class PathBoundaryError(FilesystemToolError):
    """Raised when a requested path leaves the tool root."""


class BaseFilesystemTool:
    """Resolves user paths and keeps them inside a fixed root directory."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root: Path = Path(root).resolve() if root is not None else Path.cwd().resolve()

    def _resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve()
        if not self._is_inside(resolved):
            raise PathBoundaryError(f"Path is outside the tool root: {path}")
        return resolved

    def _is_inside(self, path: Path) -> bool:
        normalized = Path(os.path.normcase(path))
        root = Path(os.path.normcase(self.root))
        return normalized == root or normalized.is_relative_to(root)
