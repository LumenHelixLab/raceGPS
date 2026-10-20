# Photo-skyline stills plan — Wave 1 (2026-09-27)

**Lane:** World Environment  
**Owner:** World Environment under Prototyper; Unreal PM gates FAIL-CLOSED  
**Worktree:** `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration` · UE **5.7**  
**Source tip:** commit `5f420f6` (`5f420f6836eb1f4af3e4666df78cce8ad0c35ccb`) — showcase skyline keepers  
**Handoff note:** `docs/handoff/2026-09-27-SHOWCASE-KEEPERS-LANDED.md`  
**Status:** PLAN LANDED — cook/load + stills capture wait on B&E editor lock + Chris Mode B / attended Track A (no unattended `LaunchClevelandRace` / Gate 1 spam)

---

## Goal

Prove the photographic Cleveland night skyline backdrop from `5f420f6` reads as Midnight Club–class distant downtown on Burke stills, using the **existing** `AClevelandEnvironmentActor` path only. No Cesium rebuild. No greenfield city. No box-skyline fallback sold as PASS when mat is present.

---

## Asset inventory (from `5f420f6`)

| Asset | Path | Role |
|-------|------|------|
| Material | `Content/Materials/M_SkylineBackdrop.uasset` → `/Game/Materials/M_SkylineBackdrop` | Unlit, two-sided, `bIsSky` (no fog); texture → emissive |
| Texture | `Content/Textures/T_Cleveland_SkylineNight.uasset` → `/Game/Textures/T_Cleveland_SkylineNight` | Night panorama |
| Source JPG | `Content/SourceImages/cleveland_skyline_night_jan2025.jpg` (7477×2227) | Import source |
| Credits | `Content/SourceImages/CREDITS.md` | CC BY 2.0 Erik Drost; Wikimedia Jan 2025 |
| Import helper | `Content/Python/import_skyline_backdrop.py` | One-shot import + mat create (path in script still points at old `racegps` tree — **do not run until path patched or run from current worktree**) |
| Mat-only helper | `Content/Python/create_skyline_backdrop_mat.py` | Rebuild mat after texture exists |

**Already on tip (no copy):** `ClevelandEnvironmentActor` photo-skyline code (`bUsePhotoSkylineBackdrop = true`, `BuildSkylineBackdrop()`). Keepers note: EnvActor matched tip before the mat/tex land.

---

## EnvActor path (reuse only)

**File:** `apps/unreal-akron-beta/Source/raceGPSAkronBeta/Private/ClevelandEnvironmentActor.cpp`  
**Header:** `.../Public/ClevelandEnvironmentActor.h`

When `bUsePhotoSkylineBackdrop` is true, `BuildSkylineBackdrop()` runs instead of procedural box skyline:

| Constant | Value | Meaning |
|----------|-------|---------|
| Center bearing | 205° | Downtown SSW of Burke (41.51722, −81.68306 → downtown ~41.499, −81.694) |
| Half span | 55° | 110° coverage |
| Radius | 260000 cm (2.6 km) | Distant card |
| Height | 60000 cm (600 m) | Building band ~0–350 m in photo |
| Base Z | −8000 cm | Photo waterline at grade |
| Segments | 64 | Arc tessellation |
| Mat load | `/Game/Materials/M_SkylineBackdrop.M_SkylineBackdrop` | Missing → log warning + return (box path only if flag false) |

Mesh: `SkylineBackdropMesh` — no collision, no shadow cast. Inward normals face the circuit.

**Hard rule:** wrap/light this path. Do **not** rebuild Cesium, City Sample, or a new downtown mesh set for this stills pass.

---

## Chris visual bar (stills scoreboard)

Burke Lakefront EZ still must read **Midnight Club / Midnight Run**:

1. **Downtown / photo skyline** — south / SSW, typically **left of frame** on race-camera stills that look toward the lake circuit.  
2. **Lake Erie** — north, typically **right of frame**.  
3. **Cars** — center, readable silhouette against skyline or asphalt, not swallowed by bloom.  
4. Empty north-facing runway with no skyline band = almost always **camera / spawn / look**, not “missing city.” Map already carries T10 HISM city + water; this pass proves the **photo backdrop card** is lit and framed.

---

## Stills plan (capture when Mode B / attended unlock)

### Preflight (B&E owns editor lock)

1. One UnrealEditor on omni — **@Build & Engine** owns the lock.  
2. Cook/load check: `M_SkylineBackdrop`, `T_Cleveland_SkylineNight` resolve; no missing-material pink on `SkylineBackdropMesh`.  
3. Log greps (forensics only, no Tier A clones):  
   - PASS cue: `photo skyline backdrop built`  
   - FAIL cue: `M_SkylineBackdrop missing; falling back to box skyline`  
4. Confirm `bUsePhotoSkylineBackdrop == true` on the level’s EnvActor (default true in header).  
5. **Do not** run unattended `LaunchClevelandRace` / Gate 1 spam — Chris owns Track A Sunset.

### Shot list (minimum set)

| ID | Intent | Framing notes | PASS if |
|----|--------|---------------|---------|
| S1 | Skyline hero | Chase or fixed cam looking roughly SSW; skyline band fills left/center horizon | Night panorama readable as Cleveland towers (not flat gray card or box stubs) |
| S2 | Lake + skyline split | Frame includes Erie water plane + skyline arc | Water north/right, skyline SSW/left; no Cesium void |
| S3 | Car photographability | Same look with vehicle in midground | Car silhouette clear; skyline not blown out; asphalt not dead black |
| S4 | Fallback control (optional) | Toggle `bUsePhotoSkylineBackdrop=false` once, still for contrast | Documented as FAIL-control only — never ship as visual PASS |

### Capture hygiene

- Attended windowed Sunset (or Chris-approved Mode B) only.  
- Evidence folder for **runtime stills / logs** when captured: prefer `docs/evidence/grokbot/burke-ez-ribbon/` for Mode B visual PASS slot (single slot — do not invent `burke-ez-visual/`).  
- This plan + inventory stay under `docs/evidence/grokbot/world-environment-training/`.  
- Screenshot + short log excerpt + commit SHA on each still. NullRHI / black void = **FAIL**.

### Lighting / look (no new systems)

- Reuse existing EnvActor look / LookDirector midnight path already on tip.  
- Cap bloom so tower lights stay discrete (see Pack 01 STEAL-MAP).  
- Do not flip `GlobalDefaultGameMode` off CruiseSprint; Showcase override only where documented.

---

## PASS / FAIL (Unreal PM FAIL-CLOSED)

| Claim | Evidence required |
|-------|-------------------|
| Keepers present on tip | Paths above exist on `5f420f6` / current tip; cite commit |
| Mat loads at runtime | Log line `photo skyline backdrop built` + no missing-mat warning |
| Stills read MC bar | S1–S3 stills under `burke-ez-ribbon/` (or dated folder Chris names) with framing notes |
| Cook/load OK | B&E log excerpt after cook; WE does not self-claim cook PASS |

**Automatic FAIL:** NullRHI, black void, pink missing mat, box skyline sold as photo PASS while mat exists, Cesium rebuild, unattended Gate 1 spam as “evidence.”

---

## Out of scope (this plan)

- Cesium / City Sample / greenfield Cleveland tourism map  
- OSM / Workshop streets (WW lane; post playable race unless unlocked)  
- Course ribbon layout (Course Architect)  
- Vehicle handling / camera code (Vehicle Arcade) — coordinate framing only  
- Patching `import_skyline_backdrop.py` hardcoded old path — note only until B&E/editor unlock needs reimport  

---

## Blockers / handoffs

| Who | Need |
|-----|------|
| **@Build & Engine** | Editor lock + cook/load of mat/tex when WE calls ready; log forensics only |
| **Chris / Prototyper** | Mode B or attended Track A for stills capture; freeze still holds on unattended launches |
| **@Unreal PM** | Gate this plan FAIL-CLOSED; unlock note in handoff when S1–S3 land |
| **@Course Architect** | No ribbon change required for this pass; WE owns hero skyline mass around existing EZ |

**WE ready for cook/load:** assets + EnvActor path inventoried; stills plan filed. Capture blocked until attended/Mode B + B&E lock.

---

## Citations

- Commit `5f420f6` / `docs/handoff/2026-09-27-SHOWCASE-KEEPERS-LANDED.md` (2026-09-27)  
- `docs/handoff/2026-09-27-BEST-OF-BOTH-RECIPE.md` — skyline keepers step DONE  
- `Content/SourceImages/CREDITS.md` — CC BY 2.0 Erik Drost  
- Pack 01 STEAL-MAP: `2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md`  
- EnvActor `BuildSkylineBackdrop()` bearing 205° / radius 2.6 km (source on tip)
