"""Filesystem tool facade for code and AI callers."""

import base64
from pathlib import Path

from pydantic import ValidationError

from rigforge.schemas.filesystem.actions import FilesystemAction
from rigforge.schemas.filesystem.requests import FilesystemRequest
from rigforge.schemas.filesystem.responses import FilesystemResponse
from rigforge.tools.filesystem.base import FilesystemToolError
from rigforge.tools.filesystem.reader import FilesystemReader
from rigforge.tools.filesystem.writer import FilesystemWriter


class FilesystemTool(FilesystemReader, FilesystemWriter):
    """Exposes filesystem actions to Python code and JSON-based AI agents."""

    def execute(
        self,
        request: FilesystemRequest | dict[str, object] | str,
    ) -> FilesystemResponse:
        """Run one request supplied as a model, a dictionary, or JSON."""
        try:
            parsed = self._parse(request)
        except ValidationError as exc:
            return FilesystemResponse(ok=False, error=exc.message)

        try:
            return self._dispatch(parsed)
        except (FilesystemToolError, OSError, ValueError) as exc:
            return FilesystemResponse(ok=False, action=parsed.action, error=str(exc))

    def execute_json(self, payload: str) -> str:
        """Run one JSON request and return a JSON response."""
        return self.execute(payload).model_dump_json()

    @staticmethod
    def _parse(
        request: FilesystemRequest | dict[str, object] | str,
    ) -> FilesystemRequest:
        if isinstance(request, FilesystemRequest):
            return request
        if isinstance(request, str):
            return FilesystemRequest.model_validate_json(request)
        return FilesystemRequest.model_validate(request)

    def _dispatch(self, request: FilesystemRequest) -> FilesystemResponse:
        match request.action:
            case FilesystemAction.PREVIEW_IMAGES:
                images = self.preview_images(request.path or ".")
                return FilesystemResponse(
                    ok=True,
                    action=request.action,
                    images=images.root,
                )
            case FilesystemAction.READ_FILE:
                data = self.read_file(self._require_path(request))
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    return FilesystemResponse(
                        ok=True,
                        action=request.action,
                        data_base64=base64.b64encode(data).decode("ascii"),
                    )
                return FilesystemResponse(ok=True, action=request.action, text=text)
            case FilesystemAction.CREATE_FILE:
                created = self.create_file(
                    self._require_path(request),
                    self._decode_content(request),
                    overwrite=request.overwrite,
                )
                return FilesystemResponse(ok=True, action=request.action, path=created)
            case FilesystemAction.CREATE_TEST_IMAGE:
                created = self.create_test_image(
                    self._require_path(request),
                    overwrite=request.overwrite,
                )
                return FilesystemResponse(ok=True, action=request.action, path=created)
            case FilesystemAction.DELETE:
                deleted = self.delete(
                    self._require_path(request),
                    recursive=request.recursive,
                )
                return FilesystemResponse(ok=True, action=request.action, path=deleted)
        raise FilesystemToolError(f"Unsupported action: {request.action}")

    @staticmethod
    def _require_path(request: FilesystemRequest) -> Path:
        if not request.path:
            raise FilesystemToolError(f"Action '{request.action}' requires a path.")
        return Path(request.path)

    @staticmethod
    def _decode_content(request: FilesystemRequest) -> bytes:
        if request.content_encoding == "base64":
            return base64.b64decode(request.content, validate=True)
        return request.content.encode("utf-8")
