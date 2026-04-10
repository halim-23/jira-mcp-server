"""MCP tool definitions and handlers for Confluence."""
from __future__ import annotations

from typing import Any

import mcp.types as types

from ..confluence_client import ConfluenceClient


def get_tools() -> list[types.Tool]:
    return [
        # ── Spaces ────────────────────────────────────────────────────────
        types.Tool(
            name="confluence_list_spaces",
            description="List all Confluence spaces accessible to the authenticated user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 25, "description": "Max number of spaces to return"},
                },
            },
        ),
        types.Tool(
            name="confluence_get_space",
            description="Get details of a Confluence space by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "Space ID"},
                },
                "required": ["space_id"],
            },
        ),
        types.Tool(
            name="confluence_get_space_by_key",
            description="Get a Confluence space by its key (e.g. 'TEAM', 'DEV').",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {"type": "string", "description": "Space key"},
                },
                "required": ["space_key"],
            },
        ),
        # ── Pages ─────────────────────────────────────────────────────────
        types.Tool(
            name="confluence_get_page",
            description="Get a Confluence page by its ID, including its body content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "body_format": {
                        "type": "string",
                        "enum": ["storage", "atlas_doc_format", "wiki"],
                        "default": "storage",
                        "description": "Body format to return",
                    },
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="confluence_list_pages_in_space",
            description="List pages in a Confluence space, optionally filtered by title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "Space ID"},
                    "title": {"type": "string", "description": "Filter by title substring"},
                    "status": {"type": "string", "default": "current", "description": "Page status: current or archived"},
                    "limit": {"type": "integer", "default": 25},
                    "cursor": {"type": "string", "description": "Pagination cursor from previous response"},
                },
                "required": ["space_id"],
            },
        ),
        types.Tool(
            name="confluence_get_child_pages",
            description="Get child pages of a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Parent page ID"},
                    "limit": {"type": "integer", "default": 25},
                    "cursor": {"type": "string", "description": "Pagination cursor"},
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="confluence_create_page",
            description=(
                "Create a new Confluence page. "
                "body_value should be Confluence Storage Format (XHTML-like). "
                "Example: '<p>Hello <strong>World</strong></p>'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "Space ID"},
                    "title": {"type": "string", "description": "Page title"},
                    "body_value": {"type": "string", "description": "Page content in Confluence Storage Format or plain text"},
                    "parent_id": {"type": "string", "description": "Parent page ID (optional)"},
                    "body_representation": {
                        "type": "string",
                        "enum": ["storage", "wiki"],
                        "default": "storage",
                        "description": "Format of body_value",
                    },
                    "status": {"type": "string", "enum": ["current", "draft"], "default": "current"},
                },
                "required": ["space_id", "title", "body_value"],
            },
        ),
        types.Tool(
            name="confluence_update_page",
            description=(
                "Update an existing Confluence page. "
                "You MUST provide the current version_number (get from confluence_get_page). "
                "The version number must be incremented by 1."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "title": {"type": "string", "description": "New title"},
                    "body_value": {"type": "string", "description": "New page content (Confluence Storage Format)"},
                    "version_number": {"type": "integer", "description": "Current version + 1"},
                    "body_representation": {
                        "type": "string",
                        "enum": ["storage", "wiki"],
                        "default": "storage",
                    },
                    "status": {"type": "string", "enum": ["current", "draft"], "default": "current"},
                },
                "required": ["page_id", "title", "body_value", "version_number"],
            },
        ),
        types.Tool(
            name="confluence_delete_page",
            description="Delete a Confluence page by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                },
                "required": ["page_id"],
            },
        ),
        # ── Labels ────────────────────────────────────────────────────────
        types.Tool(
            name="confluence_get_page_labels",
            description="Get labels on a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="confluence_add_page_labels",
            description="Add labels to a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels to add"},
                },
                "required": ["page_id", "labels"],
            },
        ),
        types.Tool(
            name="confluence_delete_page_label",
            description="Remove a label from a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "label": {"type": "string", "description": "Label to remove"},
                },
                "required": ["page_id", "label"],
            },
        ),
        # ── Search ────────────────────────────────────────────────────────
        types.Tool(
            name="confluence_search",
            description="Search Confluence content (pages, blog posts, etc.) by text query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text search query"},
                    "spaces": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Limit search to these space keys",
                    },
                    "content_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Content types to search (page, blogpost, comment, attachment)",
                    },
                    "limit": {"type": "integer", "default": 25},
                    "cursor": {"type": "string", "description": "Pagination cursor"},
                },
                "required": ["query"],
            },
        ),
        # ── Hierarchy ─────────────────────────────────────────────────────
        types.Tool(
            name="confluence_get_page_ancestors",
            description="Get the ancestor pages (breadcrumb path) of a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                },
                "required": ["page_id"],
            },
        ),
        # ── Comments ──────────────────────────────────────────────────────
        types.Tool(
            name="confluence_get_page_comments",
            description="Get footer comments on a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "limit": {"type": "integer", "default": 25},
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="confluence_add_page_comment",
            description="Add a footer comment to a Confluence page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Page ID"},
                    "body_value": {"type": "string", "description": "Comment content (Confluence Storage Format)"},
                },
                "required": ["page_id", "body_value"],
            },
        ),
    ]


def _make_text(data: Any) -> list[types.TextContent]:
    import json
    return [types.TextContent(type="text", text=json.dumps(data, indent=2, default=str))]


async def handle_tool(
    client: ConfluenceClient, tool_name: str, args: dict
) -> list[types.TextContent]:
    try:
        match tool_name:
            # Spaces
            case "confluence_list_spaces":
                data = await client.get_spaces(args.get("limit", 25))
                return _make_text(data)
            case "confluence_get_space":
                data = await client.get_space(args["space_id"])
                return _make_text(data)
            case "confluence_get_space_by_key":
                data = await client.get_space_by_key(args["space_key"])
                return _make_text(data)

            # Pages
            case "confluence_get_page":
                data = await client.get_page(args["page_id"], args.get("body_format", "storage"))
                return _make_text(data)
            case "confluence_list_pages_in_space":
                data = await client.get_pages_in_space(
                    space_id=args["space_id"],
                    title=args.get("title"),
                    status=args.get("status", "current"),
                    limit=args.get("limit", 25),
                    cursor=args.get("cursor"),
                )
                return _make_text(data)
            case "confluence_get_child_pages":
                data = await client.get_child_pages(
                    args["page_id"], args.get("limit", 25), args.get("cursor")
                )
                return _make_text(data)
            case "confluence_create_page":
                data = await client.create_page(
                    space_id=args["space_id"],
                    title=args["title"],
                    body_value=args["body_value"],
                    parent_id=args.get("parent_id"),
                    body_representation=args.get("body_representation", "storage"),
                    status=args.get("status", "current"),
                )
                return _make_text(data)
            case "confluence_update_page":
                data = await client.update_page(
                    page_id=args["page_id"],
                    title=args["title"],
                    body_value=args["body_value"],
                    version_number=args["version_number"],
                    body_representation=args.get("body_representation", "storage"),
                    status=args.get("status", "current"),
                )
                return _make_text(data)
            case "confluence_delete_page":
                await client.delete_page(args["page_id"])
                return _make_text({"status": "deleted", "page_id": args["page_id"]})

            # Labels
            case "confluence_get_page_labels":
                data = await client.get_page_labels(args["page_id"])
                return _make_text(data)
            case "confluence_add_page_labels":
                data = await client.add_page_labels(args["page_id"], args["labels"])
                return _make_text(data)
            case "confluence_delete_page_label":
                await client.delete_page_label(args["page_id"], args["label"])
                return _make_text({"status": "label_removed"})

            # Search
            case "confluence_search":
                data = await client.search(
                    query=args["query"],
                    spaces=args.get("spaces"),
                    content_types=args.get("content_types"),
                    limit=args.get("limit", 25),
                    cursor=args.get("cursor"),
                )
                return _make_text(data)

            # Hierarchy
            case "confluence_get_page_ancestors":
                data = await client.get_page_ancestors(args["page_id"])
                return _make_text(data)

            # Comments
            case "confluence_get_page_comments":
                data = await client.get_page_footer_comments(
                    args["page_id"], args.get("limit", 25)
                )
                return _make_text(data)
            case "confluence_add_page_comment":
                data = await client.create_page_comment(args["page_id"], args["body_value"])
                return _make_text(data)

            case _:
                return [types.TextContent(type="text", text=f"Unknown Confluence tool: {tool_name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
