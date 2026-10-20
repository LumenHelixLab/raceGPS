# Wave 1: WE Mode B photo-skyline stills QA (Unreal PM)

**Date:** 2026-10-05 (America/New_York), graded 22:3x ET
**Role:** Unreal PM (raceGPS)
**Gate:** World Environment Mode B photo-skyline stills, Burke EZ, Midnight preset (plan: `world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md`)
**WE self-report:** FAIL, all 4 shots
**PM verdict:** **FAIL CONFIRMED.** Not overturned, and not Gate 1 evidence. The WE self-report is honest: no false PASS.
**QA action:** Evidence-only grade. **No Unreal launches, no cook, no source or asset edits.**

---

## Evidence graded

Root: `docs/evidence/grokbot/burke-ez-ribbon/stills/`
Documents mirror: `C:\Users\cgp22\Documents\raceGPS-handoff\burke-ez-ribbon\stills\` (byte-identical, see below)

| File | Bytes | SHA256 (PM recomputed) | Matches SHA256SUMS.txt |
|---|---|---|---|
| `S1_skyline_hero_midnight_9604d0b.png` | 1690516 | `36ebf94f025b8b31f766fe9fd1df666b6a9408a3033003c7128d45baf5ab956e` | yes (repo + mirror) |
| `S2_lake_skyline_split_midnight_9604d0b.png` | 645692 | `56e45b011f731df43af9a48df762e85c6f5c7a9a1aba4b2d8441077aca22cae8` | yes (repo + mirror) |
| `S3_car_midground_midnight_9604d0b.png` | 1461866 | `1f3828081a6fb9cfa54b87bb69dd615993a1a7065bab5c8e8049b6d1d896d903` | yes (repo + mirror) |
| `S3b_car_close_midnight_9604d0b.png` | 1562977 | `434d791356918d2c88dfed3f5113b9756f8b8cef92dc13a38897bbbcea7ffab1` | yes (repo + mirror) |
| `capture_manifest_midnight_9604d0b.json` | 2655 | `199a31e1...56be371f5` | yes |
| `capture_log_excerpt_midnight_9604d0b.txt` | 8551 | `6723eb0e...241618f6e` | yes |
| `README.md` (WE report) | 5294 | `746576c9...ec170d` | yes |

Capture provenance (from log excerpt and manifest): commit `9604d0b`, branch `grokbot/cleveland-integration`. GUI UnrealEditor, editor world, PID 51808, `-d3d12`. `LogRHI: Using Forced RHI: D3D12`, SM6, AMD Radeon 880M. Shots taken 22:29:31 to 22:29:46 ET; editor exited 22:29:51 ET. `Shaders left to compile 0`. The map was not saved. The capture helper `Content/Python/_we_modeb_stills_capture.py` is untracked. Manifest verdict is `PENDING` (the script never self-claims PASS). Good.

Context also read: `world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` (S1 to S3 PASS rules, auto-FAIL list) and `burke-ez-ribbon/README.md` (09-25 ribbon slot).

---

## Auto-FAIL screen (FAIL-CLOSED)

| Auto-FAIL trigger | Result | Evidence |
|---|---|---|
| NullRHI | **Clear** | D3D12 SM6 forced RHI in log |
| Pink / missing material | **Clear** | `asset check mat=True tex=True`. Magenta pixel share is 0.00% on all 4 stills (PM pixel scan). |
| Box-skyline fallback sold as photo | **Clear (code path)** | `photo skyline backdrop built (radius 2600 m, span 110 deg)` is present. `M_SkylineBackdrop missing; falling back` is absent. `skyline_buildings=0 named_towers=0`. The black box stubs in frame are the in-map T10 HISM city rendering unlit black, not the fallback path. They still fail S1's "not box stubs" rule visually. |
| **Black void** | **TRIGGERED** | PM pixel scan, share of pixels with luma < 8: **S1 57.6%, S2 88.7%, S3 64.9%, S3b 61.6%**. Mean luma 69.8 / 18.4 / 57.2 / 63.1 matches WE's reported 70 / 18 / 57 / 63. Upper sky, ground, lake and the lower half of every frame are pure black. |
| Engine debug overlay in frame | **TRIGGERED** (disqualifying) | "YOUR SCENE CONTAINS A SKYDOME MESH WITH A SKY MATERIAL BUT IT DOES NOT COVER THAT PART OF THE SCREEN..." is tiled across all 4 stills. |

Black void alone is an automatic FAIL under the plan (§ PASS/FAIL, "Automatic FAIL").

---

## Per-shot grade (PM viewed every still)

| Shot | Plan PASS rule | PM grade | What PM sees |
|---|---|---|---|
| **S1** skyline hero (compass 205, FOV 55, eye 4 m) | Night panorama readable as Cleveland towers, not a flat card or box stubs | **FAIL** | The real panorama renders and fills the centre horizon band, but it is **rotated 180°**. Key Tower and Terminal Tower spires hang downward, and the Erie reflection band sits above the towers. It is washed out lavender. The upper 1/5 is pure black void, the lower half is black ground and debug text, and black box stubs stand in front of the card. Readable as "a city upside down", not as a Midnight Club skyline. |
| **S2** lake + skyline split (NE corner, 30 m, compass 255, FOV 100) | Erie water plane plus skyline arc; water north/right, skyline SSW/left; no void | **FAIL** | About 89% black. The inverted card covers only the right third, with a thin dark pier/shore line. **No readable Erie water plane.** Skyline is on the right, not the left (the expected side flips under UE world handedness, see RC-4). Debug overlay. |
| **S3** car midground (Showcase intro, FOV 66) | Car silhouette clear; skyline not blown out; asphalt not dead black | **FAIL** | Partial credit: the Charger reads as a clean black silhouette on the left-third midground against the bright card. Fails the other two rules: the skyline is inverted and washed out, and the asphalt is **dead black**. Debug overlay, black sky. |
| **S3b** car close (extra) | (bonus) | **FAIL** | The roof/greenhouse silhouette at bottom centre reads. Same defects as S3. |

**Midnight Club night-cruise bar:** **not met on any shot.** There is no lit street level, no wet or specular asphalt, no readable lake, an inverted skyline and a debug overlay. Nothing here is usable as a hero, marketing or Gate 1 still.

---

## Root cause (documented by WE, PM verified against source/assets)

| # | Cause | PM verification | Fix owner |
|---|---|---|---|
| **RC-1** | **Backdrop UVs are wrong. Not just V: the panorama is rotated 180° (both V and U).** | `ClevelandEnvironmentActor.cpp` L1146-1147 in `BuildSkylineBackdrop()` sets the bottom vertex (`BaseZCm`) to `V=0` and the top to `V=1`. Texture V=0 is the image top, so it renders vertically flipped. **PM addition:** a 180°-rotated crop of the S1 band matches the source JPG (`Content/SourceImages/cleveland_skyline_night_jan2025.jpg`) exactly: Key Tower (lit crown) left of Terminal Tower (pink/blue spire), same skyline order as the photo. The render is therefore also **mirrored left-right**: U=Frac runs with compass bearing, and the X=east/Y=north frame is mirrored in UE's left-handed space. **WE's "swap V" fix alone would leave a mirrored skyline** (Terminal left of Key). The fix needs top `V=0`, bottom `V=1` **and** `U = 1 - Frac` (or a global handedness fix). | **WE** (C++ source, `BuildSkylineBackdrop`) |
| **RC-2** | **`M_SkylineBackdrop` is authored with `bIsSky=true`.** | The asset `Content/Materials/M_SkylineBackdrop.uasset` (5614 B, 2026-09-09, landed in `5f420f6`) contains the serialized `bIsSky` tag. Both generators set it: `Content/Python/create_skyline_backdrop_mat.py` L23 and `Content/Python/import_skyline_backdrop.py` L37 (`is_sky True # no fog`). A 110° arc with a sky material produces the engine's "SKYDOME MESH ... DOES NOT COVER" debug overlay, seen in every frame. It likely also stops normal sky rendering in the uncovered area, which feeds RC-3's black upper sky. | **WE** (material authoring). Unlit with fog handled another way: Translucent plus Apply Fogging off, or Opaque unlit with height-fog tuning. **Not** IsSky. |
| **RC-3** | **Black void, black ground, black lake under Midnight.** | Log: `Midnight applied (22:00 moon directional)`, `sunI=2.40`, `skyI=2.20`, `V15 night ground materials applied=5`, `mids=10`, but the frames show dead black asphalt, `Water_Surface` and HISM boxes. Exposure is dominated by the bright emissive card (washed-out lavender). Partly an editor-world caveat (no GameMode/BeginPlay/PIE, editor auto-exposure), so it must be **re-verified at runtime** after RC-1 and RC-2 are fixed. | **WE** (look/exposure: Midnight sky colour or skylight floor, emissive scale on the card, night asphalt/water readability) |
| **RC-4** | **World handedness: real-geography left/right expectations are mirrored.** | WE README §4 and RC-1 above. The S2 plan rule "skyline SSW/left, water north/right" can't be met in UE frames without re-stating it or fixing handedness. | **WE plus plan author.** Re-state the S2 rule, or keep it and fix handedness globally (big; not this lane). |

**Not root causes:**
- **Cook / load (B&E):** the material and texture load (`mat=True tex=True`), the photo backdrop builds, there is no fallback and no pink. This was an editor-world capture, so cook was not in the loop. A cook fix would not change any of these stills.
- **Missing material:** no. The material is present. It is *authored wrong* (RC-2).
- **Camera:** placement is roughly correct for S1 and S3. S2's framing, and its left/right expectation, needs rework after RC-1 and RC-4. That is secondary.

---

## Recommended next fix lane

1. **Primary: WE material and backdrop path (source plus asset).** One small, attended change set:
   - In `BuildSkylineBackdrop()`: top vertex `V=0`, bottom `V=1`, `U = 1 - Frac`. Then confirm by eye against the source JPG that Key Tower is left of Terminal Tower.
   - Regenerate `M_SkylineBackdrop` **without `is_sky`** (fix both Python generators so a re-import doesn't reintroduce it). Unlit, two-sided, fog disabled by a non-sky method. Consider an emissive scalar so Midnight exposure isn't blown.
   - Midnight look: raise the sky floor so it isn't (0,0,0) above the 600 m card, and make the night asphalt and lake readable (S3 rule: "asphalt not dead black").
   - Needs a C++ rebuild plus a material asset re-save, so it needs Chris + PM green and a single editor owner. Not done in this QA.
2. **Then: WE re-capture Mode B** with the same helper, same 4 shots and same SHA discipline. Grade again here. Gate it on: no debug overlay, upright **and** non-mirrored skyline, black share well under 50%, Erie visible in S2.
3. **Camera (S2 only):** reframe after step 1, and re-state the S2 left/right rule per RC-4. Low priority.
4. **B&E cook lane:** **not** the next fix for these stills. Keep it CONDITIONAL/HOLD per `2026-10-05-TARGETED-COOK-RECIPE-QA.md`. After step 1 lands, the regenerated `M_SkylineBackdrop` will need a new load check and targeted cook.

---

## Process notes

- WE did the honest thing: a FAIL self-report, a PENDING manifest, the map left unsaved, nothing git-added, a SHA manifest and a byte-identical Documents mirror. **Honesty grade: PASS.**
- Unlock provenance: `2026-10-05-GO-UNLOCK.md` still says "Mode B / Track A still need Chris unless he expands". The stills README doesn't cite the Chris Mode B go. PM flags this for the record. It doesn't change the visual verdict.
- Freeze: one attended GUI editor run (plus a run 1 that quit with no shots), no PIE, no Launch/Gate 1, no cook. The `-ExecutePythonScript` vs `-ExecCmds="py ..."` finding (UE 5.7 quits the GUI editor after the script returns) is a useful keeper for the WE pack.

## Verdict

**FAIL CONFIRMED (S1 FAIL, S2 FAIL, S3 FAIL, S3b FAIL).** Not overturned. Root cause: inverted **and** mirrored backdrop UVs (RC-1), an IsSky-authored backdrop material (RC-2), and a Midnight black void with dead-black ground and lake (RC-3). Next lane: **WE material and backdrop source/asset fix**, then a Mode B re-capture. B&E cook isn't on the critical path for these stills.
