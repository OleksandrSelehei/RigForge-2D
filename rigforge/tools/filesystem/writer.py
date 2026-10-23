"""Write filesystem operations."""

import base64
import shutil
from pathlib import Path

from rigforge.tools.filesystem.base import BaseFilesystemTool, FilesystemToolError

_TEST_PNG: bytes = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


class FilesystemWriter(BaseFilesystemTool):
    """Creates and deletes entries inside the tool root."""

    def create_file(
        self,
        path: str | Path,
        content: bytes | str = b"",
        *,
        overwrite: bool = False,
    ) -> Path:
        """Write a file of any extension, creating parent directories."""
        target = self._resolve(path)
        if target.is_dir():
            raise IsADirectoryError(target)
        if target.exists() and not overwrite:
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return target

    def create_test_image(self, path: str | Path, *, overwrite: bool = False) -> Path:
        """Write a minimal valid 1x1 PNG image."""
        if Path(path).suffix.lower() != ".png":
            raise FilesystemToolError("Test images must use the .png extension.")
        return self.create_file(path, _TEST_PNG, overwrite=overwrite)

    def delete(self, path: str | Path, *, recursive: bool = False) -> Path:
        """Delete a file or directory inside the tool root."""
        target = self._resolve(path)
        if target == self.root:
            raise FilesystemToolError("Refusing to delete the tool root.")
        if target.is_dir():
            if recursive:
                shutil.rmtree(target)
            else:
                target.rmdir()
        elif target.exists():
            target.unlink()
        else:
            raise FileNotFoundError(target)
        return target
