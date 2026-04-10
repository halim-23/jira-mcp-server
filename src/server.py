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

# Load .env from project root (two levels up from this file)
load_dotenv(Path(__file__).parent.parent / ".env")


def _require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            "Copy .env.example to .env and fill in your credentials."
        )
    return val


def build_clients() -> tuple[JiraClient, ConfluenceClient]:
    jira = JiraClient(
        base_url=_require_env("JIRA_BASE_URL"),
        email=_require_env("JIRA_USER_EMAIL"),
        api_token=_require_env("JIRA_API_TOKEN"),
    )
    confluence = ConfluenceClient(
        base_url=os.environ.get("CONFLUENCE_BASE_URL", os.environ.get("JIRA_BASE_URL", "")),
        email=os.environ.get("CONFLUENCE_USER_EMAIL", os.environ.get("JIRA_USER_EMAIL", "")),
        api_token=os.environ.get("CONFLUENCE_API_TOKEN", os.environ.get("JIRA_API_TOKEN", "")),
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
