# raceGPS Two-App GPS Architecture — Design

**Date:** 2026-09-24  
**Status:** Approved by lead judgment (Chris: "trust u")  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration`  
**Supersedes as critical path:** hand-certified Burke / endless Chaos Cleveland grind  
**Preserves:** Frame A, citypack/pack idea, Launch override pattern, G1–G5 as reference evidence

## 1. Problem

Building a Champ Car–accurate Cleveland circuit, Chaos vehicle feel, garage, and visuals inside one Unreal editor session is too slow and too hard. The product thesis is **real GPS / street-map racing**, not survey-grade historic circuit certification.

## 2. Goals

1. Same machine, one game, **two Unreal apps**: Workshop and Race.
2. Workshop owns **garage + map builder** (GPS/OSM/area-code streets).
3. Race owns **gameplay + visuals** with maximum compute (Workshop not running).
4. Shared **pack** contract is the only bridge.
5. Prefer known arcade/GPS patterns over inventing a sim stack.

## Non-goals (v1)

- Certified 2006 Burke geometry as a ship blocker.
- Full race PIE inside Workshop.
- Online multiplayer / ZIP championship (keep rules docs; do not implement).
- AI-generated marketing video pipeline (parked).
- Two physical machines or companion phone app (format should allow later; not required for v1).

## 3. Architecture

### 3.1 Process split

| Process | Target | Responsibility |
|---------|--------|----------------|
| Workshop | `raceGPSWorkshop` | OSM/GPS import, area bbox, street route edit, garage loadouts, pack export |
| Race | `raceGPSRace` | Load pack + loadout + lighting preset; drive; AI; cameras; HUD |
| Launcher | `raceGPS.bat` or small Win UI | Start Workshop or Race; refuse Race if Workshop still holds GPU lock |

**Rule:** Only one of Workshop / Race may own the GPU at a time. Launcher detects Workshop process and prompts quit before Race.

### 3.2 Project layout

- **One** `.uproject`, **two** game targets (shared `Content/`, shared pack module).
- Modules:
  - `raceGPSPack` — read/write packs, Frame A transforms (shared).
  - `raceGPSWorkshop` — builder + garage UI (Workshop only).
  - `raceGPSRace` — pawn, AI, session, LookDirector (Race only).
  - Existing Akron/CruiseSprint code stays default for Akron path; Cleveland/GPS packs are content, not a new global GameMode default.

### 3.3 Disk layout

```
Saved/raceGPS/
  packs/<packId>/
    manifest.json
    streets.(json|xodr|bin)
    checkpoints.json
    spawn.json
    environment.json
  garage/loadouts/<loadoutId>.json
  settings.json
```

Race CLI / UI: `--pack=<id> --loadout=<id> --preset=Sunset|Twilight|Midnight`.

## 4. Pack schema (v1)

`manifest.json` required fields:

- `schemaVersion` (int, start at 1)
- `packId` (string)
- `displayName` (string)
- `frame` — Frame A: `unitsPerMeter=100`, `zUp=true`, `xEast=true`, `yNorth=true`, `originLat`, `originLon`, `originAltM`
- `source` — `{ type: "osm"|"gps_trace"|"provisional_circuit", attribution, retrievedAt, bbox }`
- `certification` — `{ status: "provisional"|"certified", notes }` (v1 always allows provisional)
- `contentHash` (sha256 of geometry files)
- `defaults` — `{ environmentPreset, loadoutId? }`

Geometry is WGS84 in files; Race converts once via Frame A double-precision helpers (G2 contract).

**Workshop writes. Race only reads.** No live network OSM inside Race.

## 5. GPS / area-code builder flow (Workshop)

1. User enters area code or city + bbox (or picks a preset region).
2. Workshop fetches or loads pinned OSM extract for bbox (roads only; configurable filters).
3. User selects a closed or point-to-point route (click streets / auto loop).
4. Workshop fillets corners, builds drivable ribbon / OpenDRIVE-ish centerline, checkpoints, spawn.
5. Optional dress: barriers, water, skyline placeholders (low cost).
6. Garage: pick car, set Engine/Grip/Brake/Weight tiers 0–5, 2-slot abilities — write loadout JSON (existing garage plan).
7. **Export pack** → `Saved/raceGPS/packs/<id>/`.
8. User quits Workshop → launches Race with that pack.

Cleveland Burke provisional pack is **one sample export**, not a unique codepath.

## 6. Race app flow

1. Cold start; load only selected pack + vehicle assets needed for loadout.
2. Apply lighting preset (Sunset / Twilight / Midnight).
3. Spawn player + optional AI count from pack/settings.
4. Arcade-fun vehicle: Chaos Arcade Control + published preset **or** drop-in arcade kit later — no endless sim tuning as critical path.
5. Session: countdown → race → checkpoints → EndRace when pack defines a circuit.

## 7. Relationship to G1–G5

| Gate | Disposition |
|------|-------------|
| G1–G2 | Keep Frame A + host evidence |
| G3 | Provisional pack = sample Workshop output shape |
| G4 | Lighting presets live in Race; Launch pattern informs Race CLI |
| G5 | 3-car EndRace proves Race session code is reusable — port patterns, do not keep Cleveland-only as the forever treadmill |

Global default GameMode remains CruiseSprint / Akron until product decides otherwise. Pack launches use **override**, never silent global rewrite.

## 8. First implementation slices (ordered)

1. **Pack module + schema + golden fixture** (pytest round-trip) — no new UI.
2. **Launcher** + empty Workshop/Race targets that boot and log `app=workshop|race`.
3. **Workshop:** bbox → OSM roads → export minimal pack (centerline + spawn).
4. **Race:** load pack → spawn arcade pawn on centerline → drive solo.
5. **Garage loadout** apply on Race boot.
6. **AI + EndRace** using G5 patterns on arbitrary packs.
7. Re-export Cleveland as a sample pack through Workshop.

## 9. Success criteria

- User can build a street route for a real bbox without opening Race.
- User can quit Workshop, start Race, and drive that pack with headroom for visuals.
- No requirement to certify historic circuits to play.
- Akron default path unbroken.

## 10. Risks

- Two targets increase build time — mitigate with shared modules and CI only building changed target when possible.
- Pack schema churn — version field + migrate once, don't silent-break Race.
- Temptation to "just PIE race in Workshop" — reject for v1; keeps GPU split honest.
