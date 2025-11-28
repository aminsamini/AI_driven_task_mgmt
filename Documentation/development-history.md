# Development History

| ID | Date | Files Modified | Description | Related ID |
| :--- | :--- | :--- | :--- | :--- |
| dehi_0001 | 2025-11-27 19:22 | `inspect_*.py`, `documentation/*.md`, `contributors/development-rules-and-path.md` | Deleted inspect files, created documentation logs, and updated SQLite rules. | N/A |
| dehi_0002 | 2025-11-27 19:30 | `main.py`, `contributors/development-rules-and-path.md` | Fixed `main.py` to use `Runner` and correct `DatabaseSessionService` initialization. Updated rules. | deim_0001 |
| dehi_0003 | 2025-11-27 21:45 | `contributors/development-rules-and-path.md` | Added Mandatory Agent Protocol (SOP) to ensure agents have full context before acting. | deim_0002 |
| dehi_0004 | 2025-11-27 21:55 | `main.py` | Modified `main.py` to accept dynamic user input instead of a hardcoded question. | N/A |
| dehi_0005 | 2025-11-27 22:15 | `main.py` | Implemented Session Memory Management with Context Compaction using `DatabaseSessionService` and a summarizer agent. | N/A |
| dehi_0006 | 2025-11-27 22:20 | `main.py` | Fixed `AttributeError` by importing `CompactionConfig` from `google.adk.agents` instead of `google.genai.types`. | deim_0003 |
| dehi_0007 | 2025-11-27 22:30 | `main.py` | Reverted Context Compaction implementation as `CompactionConfig` is not available in the installed `google-adk` version. | deim_0004 |
| dehi_0008 | 2025-11-27 16:47:30 | `main.py`, `auth.py`, `sessions.py`, `database.py`, `Documentation/development-history.md`, `Documentation/development-importance.md`, `contributors/authentication-guide.md`, `requirements.txt`, `.gitignore` | Implemented authentication system and dynamic session management. | deim_0005 |
| dehi_0009 | 2025-11-28 15:05 | `main.py` | Improved input handling in `main.py` using `sys.stdin` and `sys.stdout.flush` to prevent hangs during password entry. Added explicit prompts. | deim_0006 |
| dehi_0010 | 2025-11-28 15:10 | `main.py` | Replaced `getpass` with `sys.stdin.readline()` to resolve persistent hang issues. Password input is now visible in the terminal. | deim_0007 |
| dehi_0011 | 2025-11-28 15:14 | `requirements.txt` (verified) | Installed `bcrypt` via pip to resolve `passlib.exc.MissingBackendError`. | deim_0008 |
| dehi_0012 | 2025-11-28 15:18 | `requirements.txt` | Downgraded `bcrypt` to version 4.0.1 to resolve `AttributeError` with `passlib`. | deim_0009 |
| dehi_0013 | 2025-11-28 15:22 | `main.py` | Updated `session_service` calls (`get_session`, `delete_session`) to include the required `user_id` argument. | deim_0010 |
| dehi_0014 | 2025-11-28 15:35 | `main.py` | Restored missing `from database import init_db` import to fix `NameError`. | deim_0011 |
| dehi_0015 | 2025-11-28 15:48 | `main.py`, `config.py`, `agent_setup.py`, `session_manager.py`, `cli.py` | Refactored `main.py` into modular components for better organization and maintainability. | N/A |
| dehi_0016 | 2025-11-28 16:25 | `main.py`, `session_manager.py`, `cli.py` | Implemented Hybrid Session Management (Resume/New) and injected user identity into agent prompt. | N/A |
| dehi_0017 | 2025-11-28 16:36 | `main.py`, `session_manager.py` | Attempted to fix `user_id` persistence with manual SQL update (failed). | N/A |
| dehi_0018 | 2025-11-28 16:48 | `main.py` | Fixed `user_id` persistence by explicitly setting `session.user_id` and calling `update_session`. | N/A |
| dehi_0019 | 2025-11-28 17:00 | `database.py`, `memory_tool.py`, `agent_setup.py`, `session_manager.py`, `main.py` | Implemented structured long-term memory feature. | deim_0012 |
| dehi_0020 | 2025-11-28 17:05 | `memory_tool.py` | Corrected import path for `ToolContext` to fix `ModuleNotFoundError`. | N/A |
| dehi_0021 | 2025-11-28 17:10 | `memory_tool.py`, `agent_setup.py`, `main.py` | Refactored tool creation to use `FunctionTool` wrapper instead of `@tool` decorator to align with the installed ADK version. | N/A |
| dehi_0022 | 2025-11-28 17:15 | `memory_tool.py`, `agent_setup.py`, `main.py` | Re-applied the `FunctionTool` fix to correct a submission error. | N/A |
| dehi_0023 | 2025-11-28 17:20 | `tool_schemas.py`, `memory_tool.py` | Refactored the `save_user_info` tool to use a Pydantic model for its arguments, resolving the AFC incompatibility. | N/A |
