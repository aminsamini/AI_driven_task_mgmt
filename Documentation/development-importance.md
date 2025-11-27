# Development Importance & Issues

| ID | Date | Severity | Description | Impact | Solution | Status | Related ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| deim_0001 | 2025-11-27 19:30 | High | `main.py` used incorrect `InMemoryRunner` with `DatabaseSessionService` and incorrect initialization. | Verification failed, agent could not run with persistence. | Switched to `Runner` and fixed `DatabaseSessionService` initialization. | Solved | dehi_0002 |
| deim_0002 | 2025-11-27 21:45 | High | Agents lacked a standardized protocol for context awareness. | Risk of conflicts, redundant work, and pattern violations. | Established Mandatory Agent Protocol in `development-rules-and-path.md`. | Improved | dehi_0003 |
