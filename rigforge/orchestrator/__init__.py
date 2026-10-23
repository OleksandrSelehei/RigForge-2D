"""Pipeline orchestration shared by all front ends."""

from rigforge.config import RigForgeConfig


class Orchestrator:
    """Coordinates tools and pipelines independently of the user interface."""

    def __init__(self, config: RigForgeConfig) -> None:
        self.config = config

    def run(self) -> None:
        """Execute the default pipeline."""
        raise NotImplementedError("No pipeline is implemented yet.")
