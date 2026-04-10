"""MCP tool definitions and handlers for Jira."""
from __future__ import annotations

from typing import Any

import mcp.types as types

from ..jira_client import JiraClient


def get_tools() -> list[types.Tool]:
    return [
        # ── Projects ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_list_projects",
            description="List all accessible Jira projects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "default": 50, "description": "Maximum number of projects to return"},
                },
            },
        ),
        types.Tool(
            name="jira_get_project",
            description="Get details of a specific Jira project by its key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key (e.g. 'PROJ')"},
                },
                "required": ["project_key"],
            },
        ),
        # ── Issues ────────────────────────────────────────────────────────
        types.Tool(
            name="jira_get_issue",
            description="Get full details of a Jira issue including its status, assignee, description, comments, and available transitions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g. 'PROJ-123')"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="jira_search_issues",
            description=(
                "Search Jira issues using JQL (Jira Query Language). "
                "JQL must include at least one filter condition. "
                "Examples: 'project=PROJ AND status=Open', "
                "'assignee=currentUser() ORDER BY created DESC', "
                "'project=PROJ AND sprint in openSprints()'. "
                "Pagination uses nextPageToken from previous response."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query string (must have a filter condition, not just ORDER BY)"},
                    "max_results": {"type": "integer", "default": 50, "description": "Maximum results"},
                    "next_page_token": {"type": "string", "description": "Cursor from previous response for pagination"},
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return (omit for defaults)",
                    },
                },
                "required": ["jql"],
            },
        ),
        types.Tool(
            name="jira_create_issue",
            description=(
                "Create a new Jira issue. "
                "Provide project_key, summary, and issue_type at minimum. "
                "issue_type is usually 'Story', 'Bug', 'Task', or 'Epic'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key"},
                    "summary": {"type": "string", "description": "Issue title/summary"},
                    "issue_type": {"type": "string", "description": "Issue type name (Story, Bug, Task, Epic, Sub-task, etc.)"},
                    "description": {"type": "string", "description": "Issue description (plain text)"},
                    "priority": {"type": "string", "description": "Priority name: Highest, High, Medium, Low, Lowest"},
                    "assignee_account_id": {"type": "string", "description": "Assignee account ID"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Labels to apply"},
                    "components": {"type": "array", "items": {"type": "string"}, "description": "Component names"},
                    "fix_versions": {"type": "array", "items": {"type": "string"}, "description": "Fix version names"},
                    "story_points": {"type": "number", "description": "Story points (story_points field)"},
                    "parent_key": {"type": "string", "description": "Parent issue key (for sub-tasks or child issues)"},
                    "epic_link": {"type": "string", "description": "Epic key to link this issue to"},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                },
                "required": ["project_key", "summary", "issue_type"],
            },
        ),
        types.Tool(
            name="jira_update_issue",
            description="Update fields of an existing Jira issue. Only provide the fields you want to change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g. 'PROJ-123')"},
                    "summary": {"type": "string", "description": "New summary"},
                    "description": {"type": "string", "description": "New description (plain text)"},
                    "priority": {"type": "string", "description": "Priority name"},
                    "assignee_account_id": {"type": "string", "description": "New assignee account ID (null to unassign)"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "New labels (replaces existing)"},
                    "components": {"type": "array", "items": {"type": "string"}, "description": "New components (replaces existing)"},
                    "fix_versions": {"type": "array", "items": {"type": "string"}, "description": "New fix versions (replaces existing)"},
                    "story_points": {"type": "number", "description": "New story points"},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="jira_delete_issue",
            description="Delete a Jira issue permanently.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key to delete"},
                },
                "required": ["issue_key"],
            },
        ),
        # ── Transitions ───────────────────────────────────────────────────
        types.Tool(
            name="jira_get_transitions",
            description="Get all available workflow transitions for a Jira issue (e.g., 'In Progress', 'Done').",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="jira_transition_issue",
            description="Move a Jira issue to a new status using a workflow transition.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "transition_id": {"type": "string", "description": "Transition ID (get from jira_get_transitions)"},
                    "comment": {"type": "string", "description": "Optional comment to add on transition"},
                },
                "required": ["issue_key", "transition_id"],
            },
        ),
        # ── Comments ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_get_comments",
            description="Get all comments on a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="jira_add_comment",
            description="Add a comment to a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "comment": {"type": "string", "description": "Comment text"},
                },
                "required": ["issue_key", "comment"],
            },
        ),
        types.Tool(
            name="jira_update_comment",
            description="Update an existing comment on a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "comment_id": {"type": "string", "description": "Comment ID"},
                    "comment": {"type": "string", "description": "New comment text"},
                },
                "required": ["issue_key", "comment_id", "comment"],
            },
        ),
        types.Tool(
            name="jira_delete_comment",
            description="Delete a comment from a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "comment_id": {"type": "string", "description": "Comment ID"},
                },
                "required": ["issue_key", "comment_id"],
            },
        ),
        # ── Assignee ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_assign_issue",
            description="Assign or unassign a Jira issue. Pass null for account_id to unassign.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "account_id": {"type": ["string", "null"], "description": "Assignee account ID or null to unassign"},
                },
                "required": ["issue_key"],
            },
        ),
        # ── Users ─────────────────────────────────────────────────────────
        types.Tool(
            name="jira_search_users",
            description="Search Jira users by name or email.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Name or email query"},
                    "max_results": {"type": "integer", "default": 20},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="jira_get_current_user",
            description="Get the currently authenticated Jira user.",
            inputSchema={"type": "object", "properties": {}},
        ),
        # ── Boards ────────────────────────────────────────────────────────
        types.Tool(
            name="jira_list_boards",
            description="List Jira Agile boards, optionally filtered by project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Filter by project key"},
                    "board_type": {"type": "string", "enum": ["scrum", "kanban", "simple"], "description": "Filter by board type"},
                    "max_results": {"type": "integer", "default": 50},
                },
            },
        ),
        types.Tool(
            name="jira_get_board",
            description="Get details of a specific Jira board.",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"},
                },
                "required": ["board_id"],
            },
        ),
        types.Tool(
            name="jira_get_board_issues",
            description="Get issues on a Jira board, optionally filtered by JQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"},
                    "jql": {"type": "string", "description": "Optional JQL filter"},
                    "start_at": {"type": "integer", "default": 0},
                    "max_results": {"type": "integer", "default": 50},
                },
                "required": ["board_id"],
            },
        ),
        types.Tool(
            name="jira_get_board_backlog",
            description="Get issues in a board's backlog.",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"},
                    "jql": {"type": "string", "description": "Optional JQL filter"},
                    "start_at": {"type": "integer", "default": 0},
                    "max_results": {"type": "integer", "default": 50},
                },
                "required": ["board_id"],
            },
        ),
        # ── Sprints ───────────────────────────────────────────────────────
        types.Tool(
            name="jira_list_sprints",
            description="List sprints for a board. Filter by state: active, future, closed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"},
                    "state": {"type": "string", "enum": ["active", "future", "closed"], "description": "Sprint state filter"},
                    "max_results": {"type": "integer", "default": 50},
                },
                "required": ["board_id"],
            },
        ),
        types.Tool(
            name="jira_get_sprint",
            description="Get details of a specific sprint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "integer", "description": "Sprint ID"},
                },
                "required": ["sprint_id"],
            },
        ),
        types.Tool(
            name="jira_create_sprint",
            description="Create a new sprint on a board.",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"},
                    "name": {"type": "string", "description": "Sprint name"},
                    "goal": {"type": "string", "description": "Sprint goal"},
                    "start_date": {"type": "string", "description": "Start date (ISO 8601: 2024-01-15T08:00:00.000Z)"},
                    "end_date": {"type": "string", "description": "End date (ISO 8601: 2024-01-29T08:00:00.000Z)"},
                },
                "required": ["board_id", "name"],
            },
        ),
        types.Tool(
            name="jira_update_sprint",
            description="Update a sprint (name, goal, dates, or state). Use state='active' to start, state='closed' to complete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "integer", "description": "Sprint ID"},
                    "name": {"type": "string", "description": "New name"},
                    "goal": {"type": "string", "description": "New goal"},
                    "state": {"type": "string", "enum": ["active", "closed", "future"], "description": "New state"},
                    "start_date": {"type": "string", "description": "Start date (ISO 8601)"},
                    "end_date": {"type": "string", "description": "End date (ISO 8601)"},
                },
                "required": ["sprint_id"],
            },
        ),
        types.Tool(
            name="jira_get_sprint_issues",
            description="Get all issues in a sprint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "integer", "description": "Sprint ID"},
                    "jql": {"type": "string", "description": "Optional additional JQL filter"},
                    "max_results": {"type": "integer", "default": 50},
                },
                "required": ["sprint_id"],
            },
        ),
        types.Tool(
            name="jira_move_issues_to_sprint",
            description="Move one or more issues into a sprint.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "integer", "description": "Sprint ID"},
                    "issue_keys": {"type": "array", "items": {"type": "string"}, "description": "List of issue keys"},
                },
                "required": ["sprint_id", "issue_keys"],
            },
        ),
        types.Tool(
            name="jira_move_issues_to_backlog",
            description="Move one or more issues back to the backlog (remove from sprint).",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_keys": {"type": "array", "items": {"type": "string"}, "description": "List of issue keys"},
                },
                "required": ["issue_keys"],
            },
        ),
        # ── Metadata ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_get_issue_types",
            description="Get available issue types, optionally for a specific project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key (optional)"},
                },
            },
        ),
        types.Tool(
            name="jira_get_priorities",
            description="Get all available issue priorities.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="jira_get_fields",
            description="Get all Jira fields including custom fields.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="jira_get_labels",
            description="Get available labels in Jira.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Filter query for labels"},
                },
            },
        ),
        # ── Worklogs ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_add_worklog",
            description="Log work time against a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "time_spent": {"type": "string", "description": "Time spent (e.g. '2h', '30m', '1h 30m')"},
                    "comment": {"type": "string", "description": "Work description"},
                    "started": {"type": "string", "description": "When work started (ISO 8601)"},
                },
                "required": ["issue_key", "time_spent"],
            },
        ),
        types.Tool(
            name="jira_get_worklogs",
            description="Get all worklogs for a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                },
                "required": ["issue_key"],
            },
        ),
        # ── Watchers ──────────────────────────────────────────────────────
        types.Tool(
            name="jira_get_watchers",
            description="Get watchers of a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="jira_add_watcher",
            description="Add a user as a watcher to a Jira issue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key"},
                    "account_id": {"type": "string", "description": "Account ID to add as watcher"},
                },
                "required": ["issue_key", "account_id"],
            },
        ),
        # ── Links ─────────────────────────────────────────────────────────
        types.Tool(
            name="jira_get_link_types",
            description="Get all available issue link types (e.g. 'blocks', 'is blocked by', 'clones').",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="jira_link_issues",
            description="Create a link between two Jira issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "link_type": {"type": "string", "description": "Link type name (e.g. 'blocks', 'clones', 'Duplicate')"},
                    "inward_issue_key": {"type": "string", "description": "Inward issue key"},
                    "outward_issue_key": {"type": "string", "description": "Outward issue key"},
                    "comment": {"type": "string", "description": "Optional comment"},
                },
                "required": ["link_type", "inward_issue_key", "outward_issue_key"],
            },
        ),
    ]


def _make_text(data: Any) -> list[types.TextContent]:
    import json
    return [types.TextContent(type="text", text=json.dumps(data, indent=2, default=str))]


def _description_to_adf(text: str) -> dict:
    """Convert plain text to Atlassian Document Format."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


async def handle_tool(
    client: JiraClient, tool_name: str, args: dict
) -> list[types.TextContent]:
    try:
        match tool_name:
            # Projects
            case "jira_list_projects":
                data = await client.get_projects(args.get("max_results", 50))
                return _make_text(data)
            case "jira_get_project":
                data = await client.get_project(args["project_key"])
                return _make_text(data)

            # Issues
            case "jira_get_issue":
                data = await client.get_issue(args["issue_key"])
                return _make_text(data)
            case "jira_search_issues":
                data = await client.search_issues(
                    jql=args["jql"],
                    max_results=args.get("max_results", 50),
                    fields=args.get("fields"),
                    next_page_token=args.get("next_page_token"),
                )
                return _make_text(data)
            case "jira_create_issue":
                fields: dict[str, Any] = {
                    "project": {"key": args["project_key"]},
                    "summary": args["summary"],
                    "issuetype": {"name": args["issue_type"]},
                }
                if desc := args.get("description"):
                    fields["description"] = _description_to_adf(desc)
                if priority := args.get("priority"):
                    fields["priority"] = {"name": priority}
                if account_id := args.get("assignee_account_id"):
                    fields["assignee"] = {"accountId": account_id}
                if labels := args.get("labels"):
                    fields["labels"] = labels
                if comps := args.get("components"):
                    fields["components"] = [{"name": c} for c in comps]
                if vers := args.get("fix_versions"):
                    fields["fixVersions"] = [{"name": v} for v in vers]
                if sp := args.get("story_points"):
                    fields["story_points"] = sp
                if parent := args.get("parent_key"):
                    fields["parent"] = {"key": parent}
                if due := args.get("due_date"):
                    fields["duedate"] = due
                data = await client.create_issue({"fields": fields})
                return _make_text(data)
            case "jira_update_issue":
                fields = {}
                if summary := args.get("summary"):
                    fields["summary"] = summary
                if desc := args.get("description"):
                    fields["description"] = _description_to_adf(desc)
                if priority := args.get("priority"):
                    fields["priority"] = {"name": priority}
                if "assignee_account_id" in args:
                    fields["assignee"] = {"accountId": args["assignee_account_id"]}
                if labels := args.get("labels"):
                    fields["labels"] = labels
                if comps := args.get("components"):
                    fields["components"] = [{"name": c} for c in comps]
                if vers := args.get("fix_versions"):
                    fields["fixVersions"] = [{"name": v} for v in vers]
                if sp := args.get("story_points"):
                    fields["story_points"] = sp
                if due := args.get("due_date"):
                    fields["duedate"] = due
                await client.update_issue(args["issue_key"], {"fields": fields})
                return _make_text({"status": "updated", "issue_key": args["issue_key"]})
            case "jira_delete_issue":
                await client.delete_issue(args["issue_key"])
                return _make_text({"status": "deleted", "issue_key": args["issue_key"]})

            # Transitions
            case "jira_get_transitions":
                data = await client.get_transitions(args["issue_key"])
                return _make_text(data)
            case "jira_transition_issue":
                await client.transition_issue(
                    args["issue_key"], args["transition_id"], args.get("comment")
                )
                return _make_text({"status": "transitioned", "issue_key": args["issue_key"]})

            # Comments
            case "jira_get_comments":
                data = await client.get_comments(args["issue_key"])
                return _make_text(data)
            case "jira_add_comment":
                data = await client.add_comment(args["issue_key"], args["comment"])
                return _make_text(data)
            case "jira_update_comment":
                data = await client.update_comment(
                    args["issue_key"], args["comment_id"], args["comment"]
                )
                return _make_text(data)
            case "jira_delete_comment":
                await client.delete_comment(args["issue_key"], args["comment_id"])
                return _make_text({"status": "deleted"})

            # Assignee
            case "jira_assign_issue":
                await client.assign_issue(args["issue_key"], args.get("account_id"))
                return _make_text({"status": "assigned"})

            # Users
            case "jira_search_users":
                data = await client.search_users(args["query"], args.get("max_results", 20))
                return _make_text(data)
            case "jira_get_current_user":
                data = await client.get_current_user()
                return _make_text(data)

            # Boards
            case "jira_list_boards":
                data = await client.get_boards(
                    args.get("project_key"),
                    args.get("board_type"),
                    args.get("max_results", 50),
                )
                return _make_text(data)
            case "jira_get_board":
                data = await client.get_board(args["board_id"])
                return _make_text(data)
            case "jira_get_board_issues":
                data = await client.get_board_issues(
                    args["board_id"],
                    args.get("jql"),
                    args.get("start_at", 0),
                    args.get("max_results", 50),
                )
                return _make_text(data)
            case "jira_get_board_backlog":
                data = await client.get_board_backlog(
                    args["board_id"],
                    args.get("jql"),
                    args.get("start_at", 0),
                    args.get("max_results", 50),
                )
                return _make_text(data)

            # Sprints
            case "jira_list_sprints":
                data = await client.get_sprints(
                    args["board_id"], args.get("state"), args.get("max_results", 50)
                )
                return _make_text(data)
            case "jira_get_sprint":
                data = await client.get_sprint(args["sprint_id"])
                return _make_text(data)
            case "jira_create_sprint":
                data = await client.create_sprint(
                    board_id=args["board_id"],
                    name=args["name"],
                    goal=args.get("goal"),
                    start_date=args.get("start_date"),
                    end_date=args.get("end_date"),
                )
                return _make_text(data)
            case "jira_update_sprint":
                payload: dict[str, Any] = {}
                for key in ("name", "goal", "state", "startDate", "endDate"):
                    arg_key = key if key not in ("startDate", "endDate") else (
                        "start_date" if key == "startDate" else "end_date"
                    )
                    if val := args.get(arg_key):
                        payload[key] = val
                data = await client.update_sprint(args["sprint_id"], payload)
                return _make_text(data)
            case "jira_get_sprint_issues":
                data = await client.get_sprint_issues(
                    args["sprint_id"], args.get("jql"), args.get("max_results", 50)
                )
                return _make_text(data)
            case "jira_move_issues_to_sprint":
                await client.move_issues_to_sprint(args["sprint_id"], args["issue_keys"])
                return _make_text({"status": "moved", "sprint_id": args["sprint_id"]})
            case "jira_move_issues_to_backlog":
                await client.move_issues_to_backlog(args["issue_keys"])
                return _make_text({"status": "moved_to_backlog"})

            # Metadata
            case "jira_get_issue_types":
                data = await client.get_issue_types(args.get("project_key"))
                return _make_text(data)
            case "jira_get_priorities":
                data = await client.get_priorities()
                return _make_text(data)
            case "jira_get_fields":
                data = await client.get_fields()
                return _make_text(data)
            case "jira_get_labels":
                data = await client.get_labels(args.get("query"))
                return _make_text(data)

            # Worklogs
            case "jira_add_worklog":
                data = await client.add_worklog(
                    args["issue_key"],
                    args["time_spent"],
                    args.get("comment"),
                    args.get("started"),
                )
                return _make_text(data)
            case "jira_get_worklogs":
                data = await client.get_worklogs(args["issue_key"])
                return _make_text(data)

            # Watchers
            case "jira_get_watchers":
                data = await client.get_watchers(args["issue_key"])
                return _make_text(data)
            case "jira_add_watcher":
                await client.add_watcher(args["issue_key"], args["account_id"])
                return _make_text({"status": "watcher_added"})

            # Links
            case "jira_get_link_types":
                data = await client.get_link_types()
                return _make_text(data)
            case "jira_link_issues":
                await client.link_issues(
                    args["link_type"],
                    args["inward_issue_key"],
                    args["outward_issue_key"],
                    args.get("comment"),
                )
                return _make_text({"status": "linked"})

            case _:
                return [types.TextContent(type="text", text=f"Unknown Jira tool: {tool_name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]
