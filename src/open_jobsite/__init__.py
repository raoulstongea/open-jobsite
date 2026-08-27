"""Open Jobsite MCP server."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("open-jobsite")
except PackageNotFoundError:  # pragma: no cover - source checkout without install
    __version__ = "0.1.0"


def main() -> None:
    """Run the stdio MCP server."""
    from open_jobsite.server import cli

    cli()


__all__ = ["__version__", "main"]
