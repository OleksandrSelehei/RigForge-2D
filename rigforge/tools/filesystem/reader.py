"""Read-only filesystem operations."""

from collections import Counter
from pathlib import Path

from rigforge.schemas.filesystem.images import ImageIndex
from rigforge.tools.filesystem.base import BaseFilesystemTool

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".avif",
        ".bmp",
        ".gif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".png",
        ".svg",
        ".tif",
        ".tiff",
        ".webp",
    }
)


class FilesystemReader(BaseFilesystemTool):
    """Scans and reads files inside the tool root."""

    def preview_images(self, directory: str | Path = ".") -> ImageIndex:
        """Index every image below a directory by unique name."""
        base = self._resolve(directory)
        if not base.exists():
            raise FileNotFoundError(base)
        if not base.is_dir():
            raise NotADirectoryError(base)

        files = sorted(
            path
            for path in base.rglob("*")
            if path.is_file()
            and not path.is_symlink()
            and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        names = Counter(path.name for path in files)

        index: dict[str, Path] = {}
        for path in files:
            key = path.name if names[path.name] == 1 else f"{path.parent.name}/{path.name}"
            if key in index:
                key = path.relative_to(self.root).as_posix()
            index[key] = path
        return ImageIndex(index)

    def read_file(self, path: str | Path) -> bytes:
        """Load a file of any extension into memory."""
        target = self._resolve(path)
        if not target.is_file():
            raise FileNotFoundError(target)
        return target.read_bytes()
