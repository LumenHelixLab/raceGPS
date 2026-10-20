# Handoff: unreal-game-dev skill → Grokbot

**Artifact:** `unreal-game-dev.zip` (repo root) — a zip archive containing the `unreal-game-dev/` skill folder (SKILL.md + 8 reference files). Integrity-verified (per-file SHA-256 after extraction).

## What it is

A senior-level Unreal Engine game developer + mentor skill. Builds complete games from 5 prefabbed genre foundations — car racing, third-person shooter, MMORPG/multiplayer, platformer, top-down arena — and enforces: research-before-execution (verify engine version, hunt newer/better sources), senior game theory (MDA, core loops), UI/UX assessment on the running game, correct Chaos/CMC physics, and teach-while-building behavior.

## Install (any agent runtime)

1. Unzip `unreal-game-dev.zip` — the archive contains a top-level `unreal-game-dev/` folder.
2. Place that folder in the runtime's skills directory:
   - Kimi Work: `%APPDATA%\kimi-desktop\daimon-share\daimon\skills\`
   - Claude-compatible: `~/.claude/skills/` or project `.agents/skills/`
   - Other runtimes: wherever `SKILL.md`-format skills are loaded
3. The skill activates on requests like "build a racing game in Unreal", "prototype a third-person shooter", "teach me game dev while we build".

## Usage contract

- Entry point is `unreal-game-dev/SKILL.md` — read it first; it routes to `references/*.md` per task.
- Load references on demand, not all at once (progressive disclosure by design).
- Hard rules baked in: no "done" without runtime evidence; no orphaned background processes; no merges to the default branch without owner approval; cite sources with dates.

## raceGPS context (optional but useful)

This skill was authored on the raceGPS project (UE 5.7, C:\projects\racegps). Its research protocol and evidence discipline encode lessons from that project's black-screen campaign: pin the environment first, trust installed engine source over web tutorials, and prove everything with captured pixels.
