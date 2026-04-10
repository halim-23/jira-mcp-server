# Contributing to jira-mcp-server

Thank you for your interest in contributing! This guide will help you get up and running.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Adding New Tools](#adding-new-tools)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/jira-mcp-server.git
   cd jira-mcp-server
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/halim-23/jira-mcp-server.git
   ```

---

## Development Setup

### Requirements

- Python 3.12+
- An Atlassian account with API token ([generate one here](https://id.atlassian.com/manage-profile/security/api-tokens))

### Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure credentials

```bash
cp .env.example .env
# Fill in your Atlassian credentials in .env
```

### Run the server

```bash
python3 main.py
```

---

## Project Structure

```
jira-mcp-server/
├── main.py                        # Entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Credential template (never commit .env)
└── src/
    ├── server.py                  # MCP server wiring
    ├── jira_client.py             # Jira REST API v3 async client
    ├── confluence_client.py       # Confluence REST API v2 async client
    └── tools/
        ├── jira_tools.py          # Jira MCP tool definitions + handlers
        └── confluence_tools.py    # Confluence MCP tool definitions + handlers
```

---

## How to Contribute

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation only |

Always branch off `main`:

```bash
git checkout main
git pull upstream main
git checkout -b feature/my-new-tool
```

---

## Adding New Tools

### 1. Add the API method to the client

In `src/jira_client.py` or `src/confluence_client.py`, add an `async def` method:

```python
async def my_new_operation(self, param: str) -> dict:
    async with self._client() as c:
        r = await c.get(f"{self.base_url}/rest/api/3/some/endpoint/{param}")
        r.raise_for_status()
        return r.json()
```

### 2. Define the MCP tool

In `src/tools/jira_tools.py` (or `confluence_tools.py`), add a `types.Tool(...)` entry to `get_tools()`:

```python
types.Tool(
    name="jira_my_new_tool",
    description="Clear description of what this tool does.",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "What this param does"},
        },
        "required": ["param"],
    },
),
```

### 3. Add the handler case

In the `handle_tool()` function, add a `case`:

```python
case "jira_my_new_tool":
    data = await client.my_new_operation(args["param"])
    return _make_text(data)
```

### 4. Test it manually

```python
import asyncio, sys
sys.path.insert(0, '.')
from src.jira_client import JiraClient
from dotenv import load_dotenv
import os
load_dotenv('.env')

jira = JiraClient(os.environ['JIRA_BASE_URL'], os.environ['JIRA_USER_EMAIL'], os.environ['JIRA_API_TOKEN'])
asyncio.run(jira.my_new_operation("TEST"))
```

---

## Commit Message Convention

We follow **Conventional Commits**:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

**Types:**

| Type | When to use |
|------|-------------|
| `feat` | New tool or feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change without new feature or fix |
| `test` | Adding or updating tests |
| `chore` | Build, CI, dependency updates |

**Examples:**

```
feat(jira): add jira_get_issue_changelog tool
fix(confluence): switch search to CQL v1 endpoint
docs: update CONTRIBUTING with tool addition guide
```

---

## Pull Request Process

1. **Ensure your branch is up to date** with `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run a quick sanity check** before opening the PR:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, '.')
   from src.tools import jira_tools, confluence_tools
   print('Jira tools:', len(jira_tools.get_tools()))
   print('Confluence tools:', len(confluence_tools.get_tools()))
   "
   ```

3. **Open a Pull Request** against `main` using the provided PR template.

4. **PR checklist:**
   - [ ] Follows the branch naming convention
   - [ ] Commit messages follow Conventional Commits
   - [ ] New tool has a `types.Tool` definition with a clear `description` and `inputSchema`
   - [ ] Handler `case` is added in `handle_tool()`
   - [ ] Manually tested against a real Atlassian instance
   - [ ] `CHANGELOG.md` updated under `[Unreleased]`
   - [ ] No secrets or `.env` files committed

5. A maintainer will review and merge. Feedback will be provided inline on the PR.

---

## Reporting Bugs

Open a [Bug Report issue](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Your Python version (`python3 --version`)
- MCP SDK version (`pip show mcp`)
- The tool name that failed
- The full error message / stack trace
- Steps to reproduce (redact any credentials)

---

## Requesting Features

Open a [Feature Request issue](.github/ISSUE_TEMPLATE/feature_request.md) with:

- The Atlassian API endpoint you'd like covered
- Why it's useful
- Any relevant API documentation links

---

## Questions?

Open a [Discussion](https://github.com/halim-23/jira-mcp-server/discussions) or reach out via GitHub Issues.
