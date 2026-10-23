# Creating RigForge Tools

This document defines how every RigForge tool is built. The filesystem tool is
the reference implementation; new tools must follow the same shape and rules.

## 1. Two interfaces, one implementation

Every tool exposes exactly two public interfaces over the same internal logic:

1. **Code interface** — typed Python methods for direct use by the
   orchestrator, CLI, GUI, and tests.
2. **AI interface** — a single centralized entry point that accepts an action
   name and JSON-compatible arguments, and returns a JSON-compatible response.

The AI interface must be a thin dispatcher. It may validate input, call a typed
method, and wrap the result; it must not reimplement tool logic.

Typical AI entry points:

```python
def execute(self, request: ToolRequest | dict[str, object] | str) -> ToolResponse: ...
def execute_json(self, payload: str) -> str: ...
```

`execute` accepts a Pydantic request model, a dictionary, or a raw JSON string.
`execute_json` accepts JSON and returns JSON. The action is always selected by
the `action` field, never by a separate method name.

## 2. Package layout

Each tool lives in its own package under `rigforge/tools/`:

```
rigforge/tools/<tool_name>/
    __init__.py       # public exports
    base.py           # root/path handling, shared errors, common helpers
    <feature>.py      # one file per responsibility, e.g. reader.py, writer.py
    tool.py           # public facade, inheritance, execute/execute_json
    README.md         # usage documentation
```

DTO models live in a separate schema package under `rigforge/schemas/`:

```
rigforge/schemas/<tool_name>/
    __init__.py
    actions.py        # action enum
    requests.py       # request model
    responses.py      # response model
    <model>.py        # domain models, one per logical group
```

Rules:

- Keep `tool.py` small. It combines feature classes through inheritance and
  contains only the dispatcher.
- Split feature code into focused modules (`reader`, `writer`, `resolver`,
  `analyzer`, and so on) and inherit from a shared base when behavior is reused.
- Do not put request/response models inside `tool.py` or `base.py`. They belong
  to the schema package.
- Do not create a module per tiny helper. Split when a file has a clear,
  separate responsibility.
- Every package has an explicit `__all__` for its public surface.

## 3. Schemas and contracts

All data crossing an interface is described by Pydantic models:

- actions are a `StrEnum`;
- requests and responses are `BaseModel` subclasses;
- domain structures returned by typed methods are Pydantic models too;
- optional fields default to `None` and are handled explicitly;
- do not use `Any` where a concrete type can be expressed;
- do not return untyped dictionaries from public methods.

Responses follow one shape:

- `ok`: whether the action succeeded;
- `action`: executed action name, or `None` when parsing failed;
- typed result fields specific to the action;
- `error`: failure description, or `None`.

The typed methods raise exceptions for invalid input. The centralized
`execute`/`execute_json` interface catches expected errors and returns
`ok=False` with a message instead of raising.

## 4. Filesystem safety

Any tool that touches the filesystem must enforce a root boundary:

- the root is the current working directory at construction time;
- every user-supplied path is resolved, including `..` and symbolic links;
- a resolved path must stay inside the root;
- absolute paths are allowed only when they are inside the root;
- escaping attempts raise a dedicated boundary error;
- deleting the root itself is forbidden;
- do not follow symbolic links when scanning directories.

The boundary applies to the process that launches the tool, not to the project
source tree. A tool may go deeper inside its root, never above it.

## 5. Typing

- Annotate every function, method, argument, and return value, including
  `-> None`.
- Annotate variables when the type is not obvious from the expression.
- Use precise types: `Path`, `bytes`, enums, Pydantic models, unions.
- Handle `None`, missing files, invalid input, and boundary cases explicitly.
- Do not suppress type-checking errors, do not disable checks, and do not add
  annotations that do not match real behavior.

## 6. Minimal code

- Write the smallest solution that is correct, readable, and testable.
- Prefer direct control flow over layered abstractions.
- Do not add classes, interfaces, configuration, or files "for the future".
- Do not duplicate logic between the code and AI interfaces.
- Do not write comments that repeat the code. Document only non-obvious
  decisions and public behavior.
- Do not trade correctness, typing, security, or clarity for fewer lines.
- Keep the public API smaller than the internal implementation.

## 7. Heavy computation

- Use mature specialized libraries for numerical, vector, matrix, statistical,
  image, and scientific work: NumPy, SciPy, OpenCV, Polars/Pandas, and similar.
- Do not hand-write slow Python implementations of algorithms these libraries
  already provide.
- Pass data to libraries in large arrays; avoid per-element calls in loops.
- Do not add a heavy dependency for a trivial operation.
- Check which dependencies the project already uses before adding a new one.
- Use the standard library for ordinary business logic, file operations, and
  simple control flow.

## 8. Language and documentation

- All comments, docstrings, logs, error messages, CLI text, and documentation
  are written in English.
- Each tool has one `README.md` in its package with:
  - the security or operational boundary;
  - every action and its parameters;
  - code examples for each typed method;
  - JSON examples for each AI action;
  - the response shape and error behavior.
- The README is part of the tool. Update it in the same change as the code.

## 9. Dependencies and project rules

- Add dependencies only when the task requires them.
- Keep project configuration local; do not install system packages or change
  global environment settings.
- Run only checks and tests that are relevant to the changed tool, inside the
  project directory.
- Report what was changed and what was actually verified.

## 10. Checklist for a new tool

- [ ] Schemas are in `rigforge/schemas/<tool_name>/` and split by logic.
- [ ] Action names are defined in a `StrEnum`.
- [ ] Typed methods contain the real implementation.
- [ ] `tool.py` only combines feature classes and dispatches actions.
- [ ] `execute` accepts a model, a dictionary, and a JSON string.
- [ ] `execute_json` returns a JSON string.
- [ ] Expected failures return `ok=False` and an error message.
- [ ] Filesystem paths cannot escape the tool root.
- [ ] All Python code is fully typed.
- [ ] No unnecessary abstractions or duplicated logic.
- [ ] Heavy algorithms use specialized libraries where appropriate.
- [ ] All text in the code and docs is English.
- [ ] The tool README documents every action with examples.
- [ ] Syntax checks and relevant runtime checks pass.
