"""Actions supported by the filesystem tool."""

from enum import StrEnum


class FilesystemAction(StrEnum):
    """Name of a filesystem operation."""

    PREVIEW_IMAGES = "preview_images"
    READ_FILE = "read_file"
    CREATE_FILE = "create_file"
    CREATE_TEST_IMAGE = "create_test_image"
    DELETE = "delete"
