"""Async Confluence Cloud REST API v2 client."""
from __future__ import annotations

import base64
from typing import Any

import httpx


class ConfluenceClient:
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

    # ── Spaces ────────────────────────────────────────────────────────────────

    async def get_spaces(self, limit: int = 25) -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/spaces",
                params={"limit": limit, "sort": "name"},
            )
            r.raise_for_status()
            return r.json()

    async def get_space(self, space_id: str) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/wiki/api/v2/spaces/{space_id}")
            r.raise_for_status()
            return r.json()

    async def get_space_by_key(self, space_key: str) -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/spaces",
                params={"keys": space_key},
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            if not results:
                raise ValueError(f"Space with key '{space_key}' not found")
            return results[0]

    # ── Pages ─────────────────────────────────────────────────────────────────

    async def get_page(self, page_id: str, body_format: str = "storage") -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}",
                params={"body-format": body_format},
            )
            r.raise_for_status()
            return r.json()

    async def get_pages_in_space(
        self,
        space_id: str,
        title: str | None = None,
        status: str = "current",
        limit: int = 25,
        cursor: str | None = None,
    ) -> dict:
        params: dict[str, Any] = {
            "space-id": space_id,
            "status": status,
            "limit": limit,
        }
        if title:
            params["title"] = title
        if cursor:
            params["cursor"] = cursor
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/wiki/api/v2/pages", params=params)
            r.raise_for_status()
            return r.json()

    async def get_child_pages(
        self, page_id: str, limit: int = 25, cursor: str | None = None
    ) -> dict:
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}/children",
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def create_page(
        self,
        space_id: str,
        title: str,
        body_value: str,
        parent_id: str | None = None,
        body_representation: str = "storage",
        status: str = "current",
    ) -> dict:
        payload: dict[str, Any] = {
            "spaceId": space_id,
            "status": status,
            "title": title,
            "body": {"representation": body_representation, "value": body_value},
        }
        if parent_id:
            payload["parentId"] = parent_id
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/wiki/api/v2/pages", json=payload)
            r.raise_for_status()
            return r.json()

    async def update_page(
        self,
        page_id: str,
        title: str,
        body_value: str,
        version_number: int,
        body_representation: str = "storage",
        status: str = "current",
    ) -> dict:
        payload: dict[str, Any] = {
            "id": page_id,
            "status": status,
            "title": title,
            "body": {"representation": body_representation, "value": body_value},
            "version": {"number": version_number, "message": "Updated via MCP"},
        }
        async with self._client() as c:
            r = await c.put(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}", json=payload
            )
            r.raise_for_status()
            return r.json()

    async def delete_page(self, page_id: str) -> None:
        async with self._client() as c:
            r = await c.delete(f"{self.base_url}/wiki/api/v2/pages/{page_id}")
            r.raise_for_status()

    # ── Page Labels ───────────────────────────────────────────────────────────

    async def get_page_labels(self, page_id: str) -> dict:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/wiki/api/v2/pages/{page_id}/labels")
            r.raise_for_status()
            return r.json()

    async def add_page_labels(self, page_id: str, labels: list[str]) -> dict:
        payload = [{"prefix": "global", "name": lbl} for lbl in labels]
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}/labels", json=payload
            )
            r.raise_for_status()
            return r.json()

    async def delete_page_label(self, page_id: str, label: str) -> None:
        async with self._client() as c:
            r = await c.delete(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}/labels/{label}"
            )
            r.raise_for_status()

    # ── Search ────────────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        spaces: list[str] | None = None,
        content_types: list[str] | None = None,
        limit: int = 25,
        cursor: str | None = None,
    ) -> dict:
        """Search Confluence content using CQL via the v1 REST API."""
        cql_parts = [f'text ~ "{query}"']
        if spaces:
            space_clause = " OR ".join(f'space.key = "{s}"' for s in spaces)
            cql_parts.append(f"({space_clause})")
        if content_types:
            type_clause = " OR ".join(f'type = "{t}"' for t in content_types)
            cql_parts.append(f"({type_clause})")
        cql = " AND ".join(cql_parts) + " ORDER BY lastModified DESC"

        params: dict[str, Any] = {
            "cql": cql,
            "limit": limit,
            "expand": "space,version,ancestors",
        }
        if cursor:
            params["cursor"] = cursor
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/rest/api/content/search", params=params
            )
            r.raise_for_status()
            return r.json()

    # ── Ancestors / Hierarchy ─────────────────────────────────────────────────

    async def get_page_ancestors(self, page_id: str) -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}/ancestors"
            )
            r.raise_for_status()
            return r.json()

    # ── Comments ──────────────────────────────────────────────────────────────

    async def get_page_footer_comments(
        self, page_id: str, limit: int = 25
    ) -> dict:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/wiki/api/v2/pages/{page_id}/footer-comments",
                params={"limit": limit},
            )
            r.raise_for_status()
            return r.json()

    async def create_page_comment(self, page_id: str, body_value: str) -> dict:
        payload = {
            "pageId": page_id,
            "body": {"representation": "storage", "value": body_value},
        }
        async with self._client() as c:
            r = await c.post(
                f"{self.base_url}/wiki/api/v2/footer-comments", json=payload
            )
            r.raise_for_status()
            return r.json()
