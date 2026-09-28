# Race HUD/settings — freeze-safe plan

**Task:** 8 — Easy Test Beta
**Scope:** Cleveland race HUD and in-race settings, docs-first. This plan is an implementation contract for the later Race Systems lane; it does not merge the Akron Unreal shell, add C++, edit GameModes, launch Unreal, cook, or run PIE.

## 1. OSS research gate

- [x] OSS research reviewed before implementation planning: CommonUI/Lyra-style focus and pause flows, plus Chaos Vehicle telemetry context.
- Citation: docs/evidence/grokbot/research/2026-09-28-race-hud-oss.md (reviewed 2026-09-28; source links and applicability recorded there).
- The research is used only for interaction/data-flow ideas. It is not a dependency decision and does not authorize importing an OSS or Akron menu shell.

## 2. Akron pattern port — ideas only, no Akron shell merge

Use the existing Akron headers as behavioral references; keep Cleveland ownership, assets, maps, and launch flow separate.

- MainMenuWidget.h: retain the concept of explicit menu actions and a clear launch summary, but do not port Akron route/vehicle/LAN menus into Cleveland.
- SettingsWidget.h: mirror OnApplyClicked, OnResetClicked, and OnBackClicked; keep a pending-edit model so the race is not mutated by every slider change. Mirror the TabSwitcher concept for Graphics and Controls/Input Hints.
- OnboardingManager.h: do not invoke race onboarding. The launcher owns first-run onboarding; a race launch starts with the already-selected profile/settings and skips re-onboarding.
- PauseMenuWidget.h: mirror OnResumeClicked and OnSettingsClicked; Resume returns to the race without resetting HUD state. Restart/Quit remain explicit later decisions, not hidden side effects.
- VisualQualitySettings.h: reuse the EVisualQualityTier vocabulary (Low, Medium, High, Epic) as the graphics preset contract; Cleveland applies it through its own later implementation.
- No Akron maps, route selectors, menu GameModes, LAN browser, or full shell are merged into Cleveland.

## 3. Cleveland HUD MVP

The first freeze-safe HUD exposes only race-critical information and has stable, named widget boundaries:

| Contract | Widget | MVP behavior |
|---|---|---|
| Current vehicle speed | WBP_Speedometer | Integer **km/h** readout; clamp/format deterministically; unit label always visible. A needle/color treatment is optional polish, not a pass criterion. |
| Race phase and elapsed/lap timing | WBP_LapTimer | Clearly distinguish countdown, racing, finished, lap number, and elapsed/lap time. Freeze final values after finish. |
| Next checkpoint progress | WBP_CheckpointDistance | Show next checkpoint identity/index and distance; update on checkpoint events and make the next target unambiguous. |
| HUD composition/state | WBP_NeonHUD | Root widget owns visibility/safe-zone policy and binds race-state, speed, lap, and checkpoint updates. Loading/countdown/racing/finished states must not show stale values. |

Source stubs are the alignment surface: Content/UI/HUD/WBP_NeonHUD.txt, WBP_Speedometer.txt, plus the later WBP_LapTimer and WBP_CheckpointDistance contracts. MVP does not require minimap, drift score, nitro, weather, or tutorial overlays.

## 4. In-race settings MVP

Settings are opened from Pause and are transactional:

- **Graphics presets:** expose Low/Medium/High/Epic using EVisualQualityTier; show the selected/pending value and apply it only on Apply.
- **Input hints:** provide a compact, readable hint overlay/toggle for the active control scheme. Changing hints must not re-run launcher onboarding or alter race mode.
- **Pause flow:** Pause → Settings opens without leaving the race; Apply commits pending values and returns to Pause (or the documented settings view); Resume returns to the same race. Back with pending edits must offer Apply, Discard, or Cancel.
- **Reset:** restore documented defaults in the UI, then require Apply; never silently discard the player’s settings.
- **Freeze-safe boundary:** settings mutations are idempotent, do not recreate the race world, and do not reset timer/checkpoint/HUD state. Restart-required changes, if any, are reported rather than silently restarting.

Content/UI/Settings/WBP_Settings.txt is the UI contract; SettingsWidget.h and PauseMenuWidget.h are references, not code to merge.

## 5. Cleveland game-mode and launch rule

Cleveland is selected only by the documented LaunchClevelandRace.bat override (ClevelandShowcaseGameMode) or the equivalent packaged executable override. **Never change GlobalDefaultGameMode; it remains CruiseSprint.** Do not make HUD/settings work by changing the project default, adding a Cleveland default, or importing Akron menu maps/GameModes. Launcher Package/Dev selection must preserve this rule.

## 6. Evidence and fail-closed rule

Later runtime evidence must include the exact attended PIE or -game command/log and screenshots showing a rendered Cleveland race HUD and settings flow. A NullRHI run is not visual evidence and **NullRHI ≠ PASS**. Do not claim a visual pass from a black/empty viewport, log-only run, cook output, or an unattended Gate 1 attempt. Evidence must identify mode (Package or Dev), operator, timestamp, and artifact paths; screenshots happen only after Chris unlocks Dev launch.

## 7. Freeze order and ownership

1. **Docs + stub alignment:** freeze names, fields, state transitions, settings transaction semantics, and launch/GameMode constraints in this document and the .txt stubs. No runtime work in this task.
2. **Race Systems implementation:** when scheduled/unlocked, add the C++/WBP wiring against these contracts only; preserve the launcher-owned onboarding and Cleveland launch override. Review diffs for accidental Akron shell/GameMode changes before runtime testing.
3. **Attended Dev evidence:** after Chris unlocks Dev, run the smallest attended test, capture PIE/-game log plus non-NullRHI screenshots for HUD, Pause → Settings → Apply/Resume, and the Cleveland mode rule. Record failures honestly and do not run unattended Gate 1.

**Runtime evidence deferred to Chris unlock / attended Dev.**

## Deferred implementation checklist

- [ ] Race Systems confirms the four HUD widget contracts and state transitions.
- [ ] Settings implementation confirms pending/apply/discard behavior and EVisualQualityTier mapping.
- [ ] Attended Dev evidence records rendered screenshots and logs; no evidence is claimed by this docs-only task.
