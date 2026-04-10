"""Jira + Confluence MCP Server."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from .jira_client import JiraClient
from .confluence_client import ConfluenceClient
from .tools import jira_tools, confluence_tools

# Load .env: check cwd first (installed usage), then fall back to project root (dev usage)
load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(Path(__file__).parent.parent / ".env", override=False)


def _get_env(*names: str, required: bool = True) -> str:
    """Return the first non-empty value from the given env var names."""
    for name in names:
        val = os.environ.get(name)
        if val:
            return val
    if required:
        raise EnvironmentError(
            f"Required environment variable not set. Tried: {', '.join(names)}. "
            "Set ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN "
            "(or the legacy JIRA_BASE_URL / JIRA_USER_EMAIL / JIRA_API_TOKEN)."
        )
    return ""


def build_clients() -> tuple[JiraClient, ConfluenceClient]:
    # Accept unified ATLASSIAN_* vars (preferred) or legacy JIRA_* / CONFLUENCE_* vars
    base_url = _get_env("ATLASSIAN_URL", "JIRA_BASE_URL")
    email = _get_env("ATLASSIAN_EMAIL", "JIRA_USER_EMAIL")
    api_token = _get_env("ATLASSIAN_API_TOKEN", "JIRA_API_TOKEN")

    jira = JiraClient(base_url=base_url, email=email, api_token=api_token)
    confluence = ConfluenceClient(
        base_url=_get_env("CONFLUENCE_BASE_URL", "ATLASSIAN_URL", "JIRA_BASE_URL"),
        email=_get_env("CONFLUENCE_USER_EMAIL", "ATLASSIAN_EMAIL", "JIRA_USER_EMAIL"),
        api_token=_get_env("CONFLUENCE_API_TOKEN", "ATLASSIAN_API_TOKEN", "JIRA_API_TOKEN"),
    )
    return jira, confluence


def create_server() -> Server:
    jira_client, confluence_client = build_clients()
    server = Server("jira-mcp-server")

    all_tools = jira_tools.get_tools() + confluence_tools.get_tools()

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return all_tools

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name.startswith("jira_"):
            return await jira_tools.handle_tool(jira_client, name, arguments)
        elif name.startswith("confluence_"):
            return await confluence_tools.handle_tool(confluence_client, name, arguments)
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


async def main() -> None:
    server = create_server()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
