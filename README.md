# Jira & Confluence MCP Server

[![PyPI version](https://img.shields.io/pypi/v/atlassian-mcp.svg)](https://pypi.org/project/atlassian-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/atlassian-mcp.svg)](https://pypi.org/project/atlassian-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that lets AI assistants interact with **Jira** and **Confluence** via natural language. Works with Claude, GitHub Copilot, and any MCP-compatible client.

---

## Quick Start (Recommended)

### Install via `uvx` (no clone needed)

```bash
# 1. Get your Atlassian API token at:
#    https://id.atlassian.com/manage-profile/security/api-tokens

# 2. Add to your MCP client config:
```

```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "type": "local",
      "command": "uvx",
      "args": ["atlassian-mcp"],
      "env": {
        "ATLASSIAN_URL": "https://your-domain.atlassian.net",
        "ATLASSIAN_EMAIL": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

That's it — `uvx` automatically downloads and runs the package in an isolated environment.

> **`uvx` not installed?** Run: `pip install uv` or see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

---

## MCP Client Config Locations

| Client | Config file |
|--------|-------------|
| **GitHub Copilot CLI** | `~/.copilot/mcp-config.json` |
| **Claude Desktop (macOS)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop (Windows)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Claude Desktop (Linux)** | `~/.config/claude/claude_desktop_config.json` |

---

## Features

### Jira Tools (37 tools)

| Category | Tools |
|----------|-------|
| **Projects** | `jira_list_projects`, `jira_get_project` |
| **Issues** | `jira_get_issue`, `jira_search_issues`, `jira_create_issue`, `jira_update_issue`, `jira_delete_issue` |
| **Workflow** | `jira_get_transitions`, `jira_transition_issue` |
| **Comments** | `jira_get_comments`, `jira_add_comment`, `jira_update_comment`, `jira_delete_comment` |
| **Assignment** | `jira_assign_issue` |
| **Users** | `jira_search_users`, `jira_get_current_user` |
| **Boards** | `jira_list_boards`, `jira_get_board`, `jira_get_board_issues`, `jira_get_board_backlog` |
| **Sprints** | `jira_list_sprints`, `jira_get_sprint`, `jira_create_sprint`, `jira_update_sprint`, `jira_get_sprint_issues`, `jira_move_issues_to_sprint`, `jira_move_issues_to_backlog` |
| **Metadata** | `jira_get_issue_types`, `jira_get_priorities`, `jira_get_fields`, `jira_get_labels` |
| **Worklogs** | `jira_add_worklog`, `jira_get_worklogs` |
| **Watchers** | `jira_get_watchers`, `jira_add_watcher` |
| **Links** | `jira_get_link_types`, `jira_link_issues` |

### Confluence Tools (16 tools)

| Category | Tools |
|----------|-------|
| **Spaces** | `confluence_list_spaces`, `confluence_get_space`, `confluence_get_space_by_key` |
| **Pages** | `confluence_get_page`, `confluence_list_pages_in_space`, `confluence_get_child_pages`, `confluence_create_page`, `confluence_update_page`, `confluence_delete_page` |
| **Labels** | `confluence_get_page_labels`, `confluence_add_page_labels`, `confluence_delete_page_label` |
| **Search** | `confluence_search` |
| **Hierarchy** | `confluence_get_page_ancestors` |
| **Comments** | `confluence_get_page_comments`, `confluence_add_page_comment` |

---

## Alternative: Run from Source

```bash
git clone https://github.com/halim-23/jira-mcp-server.git
cd jira-mcp-server
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python3 main.py
```

Then point your MCP client to:
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "type": "local",
      "command": "python3",
      "args": ["atlassian-mcp"],
    }
  }
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ATLASSIAN_URL` | Your Atlassian base URL, e.g. `https://yourco.atlassian.net` |
| `ATLASSIAN_EMAIL` | Your Atlassian account email |
| `ATLASSIAN_API_TOKEN` | API token from [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens) |

All three variables are **required**. They can be set in a `.env` file (for local dev) or passed via the `env` block in your MCP client config (recommended for `uvx` usage).

---

## Example Usage

Once configured, ask your AI assistant:

- *"Show me all open issues in project MYPROJ"*
- *"Create a bug ticket: Login page throws 500 error on Safari"*
- *"Move PROJ-42 to In Progress and assign it to me"*
- *"Log 2 hours on PROJ-42 with comment 'code review'"*
- *"Show the active sprint on board 123"*
- *"Search Confluence for pages about deployment"*
- *"Create a Confluence page in space ENG titled 'API Design Guidelines'"*

---

## Technical Notes

This server targets **Jira Cloud** and **Confluence Cloud** REST APIs:

- Jira: `REST API v3` (`/rest/api/3/`) + Agile API (`/rest/agile/1.0/`)
- Confluence: `REST API v2` (`/wiki/api/v2/`) with v1 fallback for CQL search
- Search uses `POST /rest/api/3/search/jql` (the current Jira Cloud search endpoint)
- All API calls are async via `httpx`

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, requesting features, and submitting pull requests.

## License

MIT — see [LICENSE](LICENSE).
