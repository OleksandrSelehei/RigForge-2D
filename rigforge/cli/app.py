"""CLI entry point built on Typer."""

import typer

from rigforge import __version__
from rigforge.config import load_config

app = typer.Typer(
    help="RigForge-2D command line interface.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the application version."""
    typer.echo(__version__)


@app.command()
def show_config() -> None:
    """Print the resolved configuration."""
    typer.echo(load_config().model_dump_json(indent=2))


def main() -> None:
    """Run the CLI application."""
    app()
