---
name: Bug Report
about: Report a broken or misbehaving tool
title: "[BUG] <short description>"
labels: bug
assignees: halim-23
---

## Describe the Bug

A clear and concise description of what the bug is.

## Tool / Endpoint

Which MCP tool failed? (e.g. `jira_search_issues`, `confluence_create_page`)

## Steps to Reproduce

1. Call tool `...` with args `...`
2. Expected: `...`
3. Got: `...`

## Error Output

```
Paste the full error / traceback here (redact any credentials)
```

## Environment

- OS: 
- Python version (`python3 --version`): 
- MCP SDK version (`pip show mcp | grep Version`): 
- httpx version (`pip show httpx | grep Version`): 
- Atlassian product: Jira Cloud / Confluence Cloud / Jira Data Center

## Additional Context

Any other context, screenshots, or API responses that might help.
