# Filesystem Tool

`FilesystemTool` is the first RigForge tool. It provides one sandboxed set of
filesystem operations through two interfaces:

- Python code can call the typed methods directly, or use the unified
  `execute` entry point with an action name.
- AI agents call the single `execute` / `execute_json` entry point with an
  action name and JSON arguments.

## Security boundary

The tool root is the current working directory at construction time. Every
path passed to the tool is resolved, including `..` segments and symbolic
links, and must stay inside that root. Attempts to leave the root raise
`PathBoundaryError`. Paths below the root are allowed without limits.

The root itself cannot be deleted.

## Python interface

```python
from rigforge.tools.filesystem import FilesystemTool

tool = FilesystemTool()  # root = current working directory
```

`FilesystemTool(root="...")` is available for tests and embedded use. The CLI
and AI integrations should keep the default so the launch directory stays the
boundary.

### `preview_images(directory=".")`

Recursively indexes images below `directory` and returns an `ImageIndex` model.
The model is a dictionary: the key is a unique image name, the value is the
absolute path.

Supported extensions: `.avif`, `.bmp`, `.gif`, `.ico`, `.jpeg`, `.jpg`,
`.png`, `.svg`, `.tif`, `.tiff`, `.webp`.

```python
index = tool.preview_images("assets")
for name, path in index.root.items():
    print(name, path)
```

If two files have the same name, both keys are prefixed with the parent folder
name: `hero.png` becomes `characters/hero.png` and `enemies/hero.png`. If even
those keys collide, the full path relative to the tool root is used.

```python
# assets/characters/hero.png -> "characters/hero.png"
# assets/enemies/hero.png    -> "enemies/hero.png"
# assets/ui/hero.png         -> "ui/hero.png"
```

### `read_file(path)`

Loads a file of any extension into memory and returns `bytes`. Text decoding is
left to the caller.

```python
data = tool.read_file("assets/hero.png")
text = tool.read_file("notes.txt").decode("utf-8")
```

### `create_file(path, content=b"", *, overwrite=False)`

Writes a file of any extension. Missing parent directories are created
automatically. Existing files raise `FileExistsError` unless `overwrite=True`.
`content` may be `str` (encoded as UTF-8) or `bytes` (written as is).

```python
tool.create_file("tmp/notes.txt", "hello")
tool.create_file("tmp/payload.bin", b"\x00\x01\x02")
tool.create_file("tmp/notes.txt", "updated", overwrite=True)
```

### `create_test_image(path, *, overwrite=False)`

Writes a minimal valid 1x1 PNG. The path must end with `.png`. Useful for
tests and pipeline placeholders that need a real image file.

```python
tool.create_test_image("tmp/placeholder.png")
```

### `delete(path, *, recursive=False)`

Deletes a file or an empty directory. Non-empty directories require
`recursive=True`. Attempting to delete the tool root raises
`FilesystemToolError`. The deleted path is returned.

```python
tool.delete("tmp/notes.txt")
tool.delete("tmp", recursive=True)
```

## JSON interface for AI agents

`execute` accepts a `FilesystemRequest`, a dictionary, or a raw JSON string and
returns a `FilesystemResponse`. `execute_json` takes a JSON string and returns a
JSON string, which is the most convenient form for an AI tool call.

```python
payload = '{"action": "preview_images", "path": "assets"}'
response = tool.execute_json(payload)
print(response)
```

```json
{"ok":true,"action":"preview_images","images":{"hero.png":"C:\\project\\assets\\hero.png"},"path":null,"text":null,"data_base64":null,"error":null}
```

### Actions

| Action | Parameters | Response field |
| --- | --- | --- |
| `preview_images` | `path` (directory, default `.`) | `images` |
| `read_file` | `path` | `text` or `data_base64` |
| `create_file` | `path`, `content`, `content_encoding`, `overwrite` | `path` |
| `create_test_image` | `path`, `overwrite` | `path` |
| `delete` | `path`, `recursive` | `path` |

Request fields:

- `action` (required): one of the action names above.
- `path` (string, optional): target path, relative to the tool root or absolute
  inside it.
- `content` (string, default `""`): file content for `create_file`.
- `content_encoding`: `"utf-8"` (default) or `"base64"` for binary files.
- `overwrite` (boolean, default `false`): replace an existing file.
- `recursive` (boolean, default `false`): delete a non-empty directory.

### Calling actions from Python

`execute` is the single entry point for every action. Pass a dictionary, a
`FilesystemRequest`, or a JSON string; the response shape is always the same.

```python
result = tool.execute({"action": "preview_images", "path": "assets"})
if result.ok:
    for name, path in result.images.items():
        print(name, path)

result = tool.execute({"action": "read_file", "path": "notes.txt"})
content = result.text if result.text is not None else result.data_base64

result = tool.execute(
    {"action": "create_file", "path": "out/scene.json", "content": "{}"}
)
result = tool.execute(
    {
        "action": "create_file",
        "path": "out/image.png",
        "content": "iVBORw0KGgo=",
        "content_encoding": "base64",
    }
)
result = tool.execute(
    {"action": "create_test_image", "path": "tmp/placeholder.png"}
)
result = tool.execute({"action": "delete", "path": "tmp", "recursive": True})
```

The same calls can be written with the typed request model:

```python
from rigforge.schemas.filesystem import FilesystemRequest

request = FilesystemRequest(action="read_file", path="notes.txt")
result = tool.execute(request)
```

A generic wrapper is useful when the action comes from dynamic code:

```python
from rigforge.schemas.filesystem import FilesystemResponse


def call_tool(action: str, **params: object) -> FilesystemResponse:
    return tool.execute({"action": action, **params})
```

Every response exposes the same fields:

- `ok`: whether the action succeeded.
- `action`: the executed action name.
- `images`: name-to-path mapping for `preview_images`.
- `text` / `data_base64`: content for `read_file`.
- `path`: created or deleted path.
- `error`: failure description, or `None`.

### Creating files

Text content:

```python
tool.execute_json(
    '{"action": "create_file", "path": "tmp/hello.txt", "content": "hello"}'
)
```

Binary content, for example a PNG supplied by a model:

```python
tool.execute_json(
    '{"action": "create_file", "path": "tmp/generated.png", '
    '"content": "iVBORw0KGgo=", "content_encoding": "base64"}'
)
```

### Reading files

`read_file` returns UTF-8 text when the file decodes cleanly. Otherwise the
response contains `data_base64` with the raw bytes encoded as base64.

```python
tool.execute_json('{"action": "read_file", "path": "tmp/hello.txt"}')
tool.execute_json('{"action": "read_file", "path": "tmp/generated.png"}')
```

### Error handling

The typed methods raise exceptions (`PathBoundaryError`, `FileNotFoundError`,
`FileExistsError`, `FilesystemToolError`). `execute` and `execute_json` never
raise for expected failures: they return `{"ok": false, "error": "..."}` with
the action name when it is known.

```python
result = tool.execute_json('{"action": "read_file", "path": "../../secret.txt"}')
# {"ok":false,"action":"read_file","error":"Path is outside the tool root: ../../secret.txt", ...}
```
