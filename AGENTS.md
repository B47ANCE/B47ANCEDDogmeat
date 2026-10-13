# Project Zomboid Codex startup

<!-- PZ-CODEX-MANAGED-STARTUP -->
Read the current shared guide before work:
[C:\Users\willi\Desktop\Work\Project Zomboid\Codex\AGENTS.md](C:/Users/willi/Desktop/Work/Project Zomboid/Codex/AGENTS.md).

Runtime mods are Lua-only. Never implement, build, ship or require custom Java,
Java/JAR dependencies, agents, injected classes or native extensions. Use vanilla
APIs exposed to Lua; document unsupported capabilities and Lua-only alternatives.
Keep server-authoritative gameplay and sandbox configuration; dedicated G7 must
PASS before gameplay release G8. Preserve historical evidence as historical.

This folder supplies its own README, Mod ID, source layout, VERSION, tests,
dependencies and release metadata. Discover them; never import another project's
identity or roadmap. Read project-specific docs and preserve its public contracts.
State intended files/invariants before edits and run existing version checks
before/after implementation. Never invent missing versions or runtime evidence.

Shared PZ skills are available through .agents/skills. Shared tools/setup live at
C:\Users\willi\Desktop\Work\Project Zomboid\Codex; project-specific scripts take priority. Debugging does not authorize
deploy/publish. Explicit deploy/publish requests use the shared command contracts.
Server-debug is read-only SFTP; never change/restart/deploy to the remote server.
Do not launch PZ/server or mutate installed/external mods without authorization.
<!-- /PZ-CODEX-MANAGED-STARTUP -->
