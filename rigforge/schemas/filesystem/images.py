"""Image index model."""

from pathlib import Path

from pydantic import RootModel


class ImageIndex(RootModel[dict[str, Path]]):
    """Unique image name mapped to its absolute path."""
