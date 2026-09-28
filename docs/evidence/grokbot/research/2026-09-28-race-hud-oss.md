# OSS research — Race HUD/settings references

**Reviewed:** 2026-09-28 (ET)
**Purpose:** interaction and telemetry patterns only; no OSS code or Unreal shell is imported by Task 8.

- **CommonUI for Unreal Engine** — Epic documentation, accessed 2026-09-28: <https://dev.epicgames.com/documentation/en-us/unreal-engine/common-ui-plugin-for-unreal-engine>. Relevant idea: input routing, focus, and layered UI make Pause → Settings → Resume explicit and controller/keyboard friendly.
- **Lyra Starter Game** — Epic Games sample repository, accessed 2026-09-28: <https://github.com/EpicGames/Lyra>. Relevant idea: separate gameplay UI layers from menus and make state/ownership explicit.
- **Chaos Vehicles** — Epic documentation, accessed 2026-09-28: <https://dev.epicgames.com/documentation/en-us/unreal-engine/vehicles-in-unreal-engine>. Relevant idea: vehicle telemetry should feed presentation widgets through a narrow data contract; it does not prescribe Cleveland HUD art or GameMode changes.

**Task 8 decision:** use only the ideas above as review prompts. Cleveland remains responsible for WBP_NeonHUD, speed km/h, lap/race state, checkpoint distance, and transactional in-race settings.
