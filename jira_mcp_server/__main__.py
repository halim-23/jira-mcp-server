"""Jira + Confluence MCP Server — entry point for uvx / pipx."""
import asyncio
import sys


def run() -> None:
    """Console script entry point: ``jira-mcp-server``."""
    from jira_mcp_server.server import main  # noqa: PLC0415
    asyncio.run(main())


if __name__ == "__main__":
    run()
