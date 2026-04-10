#!/usr/bin/env python3
"""Entry point for the Jira MCP server."""
import asyncio
from src.server import main

if __name__ == "__main__":
    asyncio.run(main())
