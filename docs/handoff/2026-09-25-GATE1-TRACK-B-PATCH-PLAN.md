# Gate 1 Track B — instrumentation patch plan (no mass launches)

**Status:** PLAN ONLY until Prototyper/Chris green a build + **attended** Track A repro.  
**Goal:** Prove why GameViewport dies ~2s after Racing (ownership vs slate close vs other).

## Success criteria

Attended Sunset `-game` windowed (human bat, Chris focused):
1. Logs show ordered stamps: Racing → (optional deactivate) → viewport lost reason — **or** no viewport lost and session survives.
2. If ViewportClosed still fires: log names which path nullified viewport (window closed / deactivate / engine clear) with race state + focus flags.
3. Still **FAIL** if black void / NullRHI — this plan is for a real window.

## Where to instrument (temporary)

### A. Lightweight GameMode tick probe (lowest risk)
**File:** `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/ClevelandShowcaseGameMode.cpp`  
**In** `Tick` once session ≥ Racing:

- Each 1s (or on edge): log `World->GetGameViewport() != nullptr`, `GEngine->GameViewport` validity, `FApp::HasFocus()`, current race state enum.
- One-shot Warning when viewport becomes invalid while state==Racing (last line before engine exit if possible).

### B. Viewport client deactivate/close hooks (preferred signal)
Temporary subclass e.g. `UClevelandDigViewportClient` : `UGameViewportClient`:
- Override focus lost / window close requested (confirm exact UE 5.7 virtuals in local `GameViewportClient.h` before coding).
- UE_LOG Warning with reason + race state.
- Register via Showcase GameMode / Showcase-only config — **do not** change CruiseSprint global defaults.

### C. Do not change yet
- playtest RequestExit ~L415 / ~L620
- RestartShowcase / human EndRace path
- LaunchClevelandRace.bat human default (document only)
- GlobalDefaultGameMode

## Bat / launch hygiene

Human default: `start "…" UnrealEditor … -game` + preset + `-log -windowed -ResX=1600 -ResY=900` (no AutoLap).  
Track A: Chris runs via Explorer double-click. Agents: **no** unattended Start-Process for Gate 1.  
Optional later (only if attended still dies): one attended fullscreen trial.

## Build / verify

1. Build raceGPSAkronBeta Editor target (single editor owner on omni).
2. Chris Track A: LaunchClevelandRace.bat Sunset — keep focus.
3. Collect Saved/Logs excerpt → `docs/evidence/grokbot/G6-race-base-mvp/track-b-attended-*.log` + short note.
4. Interpret:
   - Survives without viewport-lost → ownership root cause; Gate 1 proof is attended-only.
   - Viewport-lost stamps while focused → targeted fix from stamp (not shotgun).
5. Strip TEMP logs after dig closes.

## Out of scope

Burke stills, Vehicle Arcade handling, ForceFinish nullrhi PASS claims, Course Architect editor.
