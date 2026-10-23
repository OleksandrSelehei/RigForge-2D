"""Tool contracts used by the orchestrator."""

from typing import Protocol


class Tool(Protocol):
    """Interface implemented by every RigForge tool."""

    name: str

    def run(self) -> None:
        """Execute the tool."""
        ...
