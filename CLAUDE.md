# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Agent chat application with a Python Flask backend and Vue 3 frontend. Uses OpenAI-compatible API (configured for Xiaomi MiMo). Supports multi-turn conversation, tool calling (web search, calculator), image upload, and conversation persistence.

## Development Commands

```bash
# Backend (Flask, port 5000)
python app.py

# Frontend (Vite, port 5173, proxies /api to Flask)
cd frontend && npm run dev

# Production build
cd frontend && npm run build
# Then: python app.py (serves static files from frontend/dist)
```

## Architecture

```
Frontend (Vue 3)          Backend (Flask)           Agent Core
App.vue                   app.py                    agent/core.py
├─ Sidebar.vue            /api/chat ──────────────→ Agent.chat()
├─ ChatWindow.vue         /api/conversations        ├─ LLM API call (requests)
└─ api.js (axios)         /api/models               ├─ tool_calls → tools/
                                                    └─ summary compression
```

**Message flow:** User input → `api.js` POST to `/api/chat` → Flask creates `Agent`, restores history → `Agent.chat()` loops: call LLM → if tool_calls, execute tool and re-call LLM (max 10 turns) → return `{thinking, content}` → frontend displays + auto-saves conversation.

**Agent loop:** Each user message triggers potentially multiple LLM API calls. LLM returns `tool_calls` → agent executes tools → feeds results back → LLM generates final response. Simple messages only need 1 API call.

**Memory:** Full conversation history passed in each request. Summary compression triggers automatically when token count exceeds `summary_token_limit` (config.yaml), compressing older messages into a summary while keeping recent ~`summary_keep_tokens` intact.

## Key Files

- `agent/core.py` — Agent class: LLM calling, tool execution loop, token estimation, summary compression
- `tools/base.py` — `BaseTool` ABC: define `name`, `description`, `parameters` (JSON Schema), `execute()`. `schema` property auto-generates OpenAI function calling format
- `app.py` — Flask routes, creates Agent per request, restores conversation history from frontend
- `utils/config.py` — Reads `config.yaml` (API config, models, agent settings)
- `utils/conversation.py` — Conversation persistence (JSON files in `conversations/`)
- `frontend/src/api.js` — All backend API calls via axios
- `frontend/src/App.vue` — Main state management (conversation list, model selection, send/save logic)

## Adding a New Tool

1. Create file in `tools/`, inherit `BaseTool`, implement `name`, `description`, `parameters`, `execute()`
2. Register in `app.py` `create_agent()`: `agent.register_tool(MyTool())`
3. Update `config.yaml` `system_prompt` to inform the AI about the new tool

## Configuration

`config.yaml` (gitignored, copy from `config.yaml.example`):
- `api.base_url` / `api_key` — OpenAI-compatible endpoint
- `models` — available model list (name + label)
- `agent.system_prompt` — AI role definition
- `agent.max_turns` — max tool call loops per message (default 10)
- `agent.summary_token_limit` — trigger compression threshold (default 40000)
- `agent.summary_keep_tokens` — recent messages to preserve (default 8000)

## Conventions

- Backend is synchronous Flask; LLM calls use `requests` with 60s timeout
- Frontend uses Vue 3 Composition API (`<script setup>`)
- All API responses are JSON
- Logs go to `logs/` directory (date-based files)
- Chinese UI and comments throughout
