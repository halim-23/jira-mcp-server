"""Async Jira Cloud REST API v3 client."""
from __future__ import annotations

import base64
from typing import Any

import httpx


class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers, timeout=30)

    # ── Projects ──────────────────────────────────────────────────────────────

    async def get_projects(self, max_results: int = 50) -> list[dict]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/api/3/project/search",
                params={"maxResults": max_results, "expand": "description,lead"},
            )
            r.raise_for_status()
            return r.json().get("values", [])

    async def get_project(self, project_key: str) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/project/{project_key}")
            r.raise_for_status()
            return r.json()

    # ── Issues ────────────────────────────────────────────────────────────────

    async def get_issue(self, issue_key: str) -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                params={"expand": "renderedFields,transitions,changelog"},
            )
            r.raise_for_status()
            return r.json()

    async def create_issue(self, payload: dict) -> dict:
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/rest/api/3/issue", json=payload)
            r.raise_for_status()
            return r.json()

    async def update_issue(self, issue_key: str, payload: dict) -> None:
        async with self._client() as c:
            r = await c.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}", json=payload
            )
            r.raise_for_status()

    async def delete_issue(self, issue_key: str) -> None:
        async with self._client() as c:
            r = await c.delete(f"{self.base_url}/rest/api/3/issue/{issue_key}")
            r.raise_for_status()

    async def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: list[str] | None = None,
        next_page_token: str | None = None,
    ) -> dict:
        """Search issues via /rest/api/3/search/jql (cursor-based pagination).

        NOTE: JQL must include at least one filter condition, not just ORDER BY.
        Unbounded JQL (e.g. just 'ORDER BY updated DESC') will automatically
        get 'project is not EMPTY' prepended.
        """
        default_fields = fields or [
            "summary", "status", "assignee", "reporter", "priority",
            "issuetype", "created", "updated", "description", "labels",
            "components", "fixVersions", "sprint",
        ]
        # Guard against unbounded JQL (Jira rejects queries without a filter)
        jql_stripped = jql.strip()
        if jql_stripped.upper().startswith("ORDER BY") or not jql_stripped:
            jql = f"project is not EMPTY {jql}"

        body: dict[str, Any] = {
            "jql": jql,
            "maxResults": max_results,
            "fields": default_fields,
        }
        if next_page_token:
            body["nextPageToken"] = next_page_token

        async with self._client() as c:
            r = await c.post(f"{self.base_url}/rest/api/3/search/jql", json=body)
            r.raise_for_status()
            return r.json()

    # ── Transitions ───────────────────────────────────────────────────────────

    async def get_transitions(self, issue_key: str) -> list[dict]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
            )
            r.raise_for_status()
            return r.json().get("transitions", [])

    async def transition_issue(self, issue_key: str, transition_id: str, comment: str | None = None) -> None:
        body: dict[str, Any] = {"transition": {"id": transition_id}}
        if comment:
            body["update"] = {
                "comment": [{"add": {"body": {"type": "doc", "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]}}}]
            }
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions", json=body
            )
            r.raise_for_status()

    # ── Comments ──────────────────────────────────────────────────────────────

    async def get_comments(self, issue_key: str) -> list[dict]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/issue/{issue_key}/comment")
            r.raise_for_status()
            return r.json().get("comments", [])

    async def add_comment(self, issue_key: str, text: str) -> dict:
        body = {
            "body": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
            }
        }
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/comment", json=body
            )
            r.raise_for_status()
            return r.json()

    async def update_comment(self, issue_key: str, comment_id: str, text: str) -> dict:
        body = {
            "body": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
            }
        }
        async with self._client() as c:
            r = await c.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/comment/{comment_id}",
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def delete_comment(self, issue_key: str, comment_id: str) -> None:
        async with self._client() as c:
            r = await c.delete(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/comment/{comment_id}"
            )
            r.raise_for_status()

    # ── Assignee ──────────────────────────────────────────────────────────────

    async def assign_issue(self, issue_key: str, account_id: str | None) -> None:
        async with self._client() as c:
            r = await c.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/assignee",
                json={"accountId": account_id},
            )
            r.raise_for_status()

    # ── Users ─────────────────────────────────────────────────────────────────

    async def search_users(self, query: str, max_results: int = 20) -> list[dict]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/api/3/user/search",
                params={"query": query, "maxResults": max_results},
            )
            r.raise_for_status()
            return r.json()

    async def get_current_user(self) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/myself")
            r.raise_for_status()
            return r.json()

    # ── Boards (Agile) ────────────────────────────────────────────────────────

    async def get_boards(
        self,
        project_key: str | None = None,
        board_type: str | None = None,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {"maxResults": max_results}
        if project_key:
            params["projectKeyOrId"] = project_key
        if board_type:
            params["type"] = board_type
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/agile/1.0/board", params=params)
            r.raise_for_status()
            return r.json()

    async def get_board(self, board_id: int) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/agile/1.0/board/{board_id}")
            r.raise_for_status()
            return r.json()

    async def get_board_issues(
        self,
        board_id: int,
        jql: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {"startAt": start_at, "maxResults": max_results}
        if jql:
            params["jql"] = jql
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/agile/1.0/board/{board_id}/issue", params=params
            )
            r.raise_for_status()
            return r.json()

    async def get_board_backlog(
        self,
        board_id: int,
        jql: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {"startAt": start_at, "maxResults": max_results}
        if jql:
            params["jql"] = jql
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/agile/1.0/board/{board_id}/backlog",
                params=params,
            )
            r.raise_for_status()
            return r.json()

    # ── Sprints ───────────────────────────────────────────────────────────────

    async def get_sprints(
        self, board_id: int, state: str | None = None, max_results: int = 50
    ) -> dict:
        params: dict[str, Any] = {"maxResults": max_results}
        if state:
            params["state"] = state
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint",
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def get_sprint(self, sprint_id: int) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}")
            r.raise_for_status()
            return r.json()

    async def create_sprint(
        self,
        board_id: int,
        name: str,
        goal: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {"name": name, "originBoardId": board_id}
        if goal:
            body["goal"] = goal
        if start_date:
            body["startDate"] = start_date
        if end_date:
            body["endDate"] = end_date
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/rest/agile/1.0/sprint", json=body)
            r.raise_for_status()
            return r.json()

    async def update_sprint(self, sprint_id: int, payload: dict) -> dict:
        async with self._client() as c:
            r = await c.put(
                f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}", json=payload
            )
            r.raise_for_status()
            return r.json()

    async def get_sprint_issues(
        self, sprint_id: int, jql: str | None = None, max_results: int = 50
    ) -> dict:
        params: dict[str, Any] = {"maxResults": max_results}
        if jql:
            params["jql"] = jql
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def move_issues_to_sprint(self, sprint_id: int, issue_keys: list[str]) -> None:
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
                json={"issues": issue_keys},
            )
            r.raise_for_status()

    async def move_issues_to_backlog(self, issue_keys: list[str]) -> None:
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/agile/1.0/backlog/issue",
                json={"issues": issue_keys},
            )
            r.raise_for_status()

    # ── Metadata ──────────────────────────────────────────────────────────────

    async def get_issue_types(self, project_key: str | None = None) -> list[dict]:
        async with self._client() as c:
            if project_key:
                r = await c.get(
                    f"{self.base_url}/rest/api/3/issuetype/project",
                    params={"projectId": project_key},
                )
            else:
                r = await c.get(f"{self.base_url}/rest/api/3/issuetype")
            r.raise_for_status()
            return r.json()

    async def get_priorities(self) -> list[dict]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/priority")
            r.raise_for_status()
            return r.json()

    async def get_fields(self) -> list[dict]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/field")
            r.raise_for_status()
            return r.json()

    # ── Labels ────────────────────────────────────────────────────────────────

    async def get_labels(self, query: str | None = None) -> list[str]:
        params: dict[str, Any] = {}
        if query:
            params["query"] = query
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/label", params=params)
            r.raise_for_status()
            data = r.json()
            return data.get("values", [])

    # ── Worklogs ──────────────────────────────────────────────────────────────

    async def add_worklog(
        self,
        issue_key: str,
        time_spent: str,
        comment: str | None = None,
        started: str | None = None,
    ) -> dict:
        body: dict[str, Any] = {"timeSpent": time_spent}
        if comment:
            body["comment"] = {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }
        if started:
            body["started"] = started
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/worklog", json=body
            )
            r.raise_for_status()
            return r.json()

    async def get_worklogs(self, issue_key: str) -> list[dict]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/issue/{issue_key}/worklog")
            r.raise_for_status()
            return r.json().get("worklogs", [])

    # ── Watchers ──────────────────────────────────────────────────────────────

    async def get_watchers(self, issue_key: str) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/issue/{issue_key}/watchers")
            r.raise_for_status()
            return r.json()

    async def add_watcher(self, issue_key: str, account_id: str) -> None:
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/watchers",
                json=account_id,
            )
            r.raise_for_status()

    # ── Links ─────────────────────────────────────────────────────────────────

    async def get_link_types(self) -> list[dict]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/rest/api/3/issueLinkType")
            r.raise_for_status()
            return r.json().get("issueLinkTypes", [])

    async def link_issues(
        self,
        link_type: str,
        inward_issue_key: str,
        outward_issue_key: str,
        comment: str | None = None,
    ) -> None:
        body: dict[str, Any] = {
            "type": {"name": link_type},
            "inwardIssue": {"key": inward_issue_key},
            "outwardIssue": {"key": outward_issue_key},
        }
        if comment:
            body["comment"] = {
                "body": {
                    "type": "doc", "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
                }
            }
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/rest/api/3/issueLink", json=body)
            r.raise_for_status()
