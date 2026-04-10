# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-10

### Added
- Initial release of the Jira & Confluence MCP Server
- **Jira** — 37 tools covering projects, issues (CRUD), workflow transitions,
  comments, users, boards, sprints, worklogs, watchers, and issue links
- **Confluence** — 16 tools covering spaces, pages (CRUD), labels, CQL search,
  page hierarchy, and comments
- Async HTTP client using `httpx` for all Atlassian REST API calls
- Jira Cloud REST API v3 support (`/rest/api/3/` and `/rest/agile/1.0/`)
- Confluence Cloud REST API v2 support (`/wiki/api/v2/`) with CQL search via v1
- Environment-based configuration via `.env` file
- Auto-bounds unbounded JQL queries to comply with Jira's query restrictions
