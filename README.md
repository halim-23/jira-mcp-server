# Jira & Confluence MCP Server

An MCP (Model Context Protocol) server that lets AI assistants interact with **Jira** and **Confluence** via natural language.

## Features

### Jira Tools (35+ tools)

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

### Confluence Tools (15+ tools)

| Category | Tools |
|----------|-------|
| **Spaces** | `confluence_list_spaces`, `confluence_get_space`, `confluence_get_space_by_key` |
| **Pages** | `confluence_get_page`, `confluence_list_pages_in_space`, `confluence_get_child_pages`, `confluence_create_page`, `confluence_update_page`, `confluence_delete_page` |
| **Labels** | `confluence_get_page_labels`, `confluence_add_page_labels`, `confluence_delete_page_label` |
| **Search** | `confluence_search` |
| **Hierarchy** | `confluence_get_page_ancestors` |
| **Comments** | `confluence_get_page_comments`, `confluence_add_page_comment` |

## Setup

### 1. Install dependencies

```bash
cd jira-mcp-server
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your Atlassian credentials
```

Get your API token at: https://id.atlassian.com/manage-profile/security/api-tokens

```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Confluence (usually same domain — you can omit these if same as Jira)
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_USER_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

### 3. Add to your MCP client config

For **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "python3",
      "args": ["/path/to/jira-mcp-server/main.py"]
    }
  }
}
```

Or pass credentials via env in the config (see `mcp_config.example.json`).

### 4. Run manually (for testing)

```bash
python3 main.py
```

## Project Structure

```
jira-mcp-server/
├── main.py                        # Entry point
├── requirements.txt
├── .env.example                   # Credential template
├── mcp_config.example.json        # MCP client config example
└── src/
    ├── server.py                  # MCP server wiring
    ├── jira_client.py             # Jira REST API v3 client
    ├── confluence_client.py       # Confluence REST API v2 client
    └── tools/
        ├── jira_tools.py          # Jira tool definitions + handlers
        └── confluence_tools.py    # Confluence tool definitions + handlers
```

## Usage Examples

> **Create a bug:**
> "Create a bug in project MYPROJ titled 'Login fails on mobile' with high priority"

> **Sprint management:**
> "Show me all active sprints on board 42, then move PROJ-101 and PROJ-102 into the current sprint"

> **Transition an issue:**
> "Move PROJ-456 to Done and add a comment saying it was fixed in v2.1"

> **Confluence:**
> "Create a page in the TEAM space titled 'Sprint 42 Retrospective' with a summary of what went well"

> **Search:**
> "Find all unresolved bugs assigned to me in the BACKEND project"

## Authentication

Uses **Basic Auth** with an Atlassian API token (not your password). Works with Jira Cloud and Confluence Cloud.

For **Jira Data Center / Server**, you may need to adjust the API base paths in the client files.
