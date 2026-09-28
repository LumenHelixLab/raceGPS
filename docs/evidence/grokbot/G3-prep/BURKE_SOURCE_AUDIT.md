# G3 Prep — Burke Lakefront / Grand Prix of Cleveland source audit

**Auditor:** Grok Bot (read-only)  
**UTC written:** 2026-09-07T21:46Z (5:46 PM ET)  
**Hosts inspected:** `C:\projects\racegps` (primary request) and mission worktree `C:\projects\raceGPS-grokbot-cleveland`  
**Scope:** Historical course source register + G3 certification blockers. No Unreal build. No commit.  
**Provisional G3 reference year (handoff/contract):** **2006 Grand Prix of Cleveland** at Burke Lakefront Airport (BKL).  
**Disposition:** **BLOCKED for G3 certification** — provisional reconstruction and contemporary context exist; dated georeferenced 2006 course plan + temporary boundaries do not.

---

## 1. Year / geometry distinctions (do not conflate)

| Label | Years | Official length | Turns | Relation to 2006 |
|---|---|---|---|---|
| **1982 Cleveland 500 / Budweiser Cleveland 500 (original)** | 1982–1989 (practice into 1990) | ~2.48 mi / 3.991 km | 12 (ECH: 8R/4L) | **Different geometry.** Includes post-pits left-right T1/T2 kink later deleted. |
| **1990 race – 1996 published** | 1990 race onward | Published 2.369 mi / ~3.812–3.813 km | 10 | Same **driven** family as later years after T1/T2 bypass; published length later treated as wrong by gdecarli. |
| **1997–2007 remeasured (pack era)** | 1997–2007 | **2.106 mi / 3389 m** | 10, clockwise | **Same layout family as 2006.** Sources state **no visible layout change** in 1997 — remeasure only. |
| **2006 Grand Prix of Cleveland** (G3 target) | 25 Jun 2006 | 2.106 mi family | 10 | Champ Car; winner A.J. Allmendinger (ChampCarStats). Uses **1990+ / 1997–2007** geometry, **not** 1982. |
| Other years | e.g. 2003 night race, 2007 final year | same 2.106 family | 10 | Same layout family; do not invent downtown streets. |

**Rules for claims**
- Do **not** label the in-repo pack as the **1982 Cleveland 500** layout.
- Do **not** claim the reconstructed centerline is a **surveyed 2006 racing line** until a dated plan / controls are georeferenced and compared.
- Branding: product remains **raceGPS: Cleveland Historic Circuit** (no historical title-sponsor strings in UI).

**Web corroboration (2026-09-07 fetch/search; secondary)**
- Wikipedia *Grand Prix of Cleveland*: 1982–89 2.480 mi; 1990 bypass T1/T2 → 2.369 mi; 1997 remeasure → 2.106 mi; 2006 = 25th running.
- gdecarli Burke: 1990+ layout still in use as of 2006; 1997 length correction without layout change.
- Motor Sport Magazine: 1990–2007 selector; length 2.106 mi; 2006 race lap note (Nelson Philippe).
- Encyclopedia of Cleveland History: original Budweiser-Cleveland 500; 2.48 mi / 12 turns origin story; later 10-turn ~2.37 mi mention (era language — reconcile with 2.106 remeasure).
- ChampCarStats: length eras 2.48 / 2.369 / 2.106; 2006 race listed 6/25/2006.

---

## 2. Split inventory across trees (critical)

| Asset | `C:\projects\racegps` | `C:\projects\raceGPS-grokbot-cleveland` |
|---|---|---|
| `docs/CLEVELAND_TRACK_PROVENANCE.md` | **Present** | Absent |
| `docs/CLEVELAND_DEMO.md` (+ other CLEVELAND_*) | **Present** | Absent |
| Playable historic pack `burke_gp_1997/` | **Present** under `apps/unreal-akron-beta/citypacks/cleveland/` | **Absent** |
| `scripts/build_cleveland_circuit.py` + `tests/test_cleveland_circuit.py` | **Present** | Absent |
| `data/sources/cleveland-burke/` (pinned OSM) | **Absent** | **Present** |
| `docs/plans/CLEVELAND_REFERENCE_CONTRACT.md` | Absent | **Present** |
| `docs/evidence/` (D1 / next-five-gates / grokbot) | Absent | **Present** |
| Root `citypacks/cleveland/burke_gp_1997` (path tests/script expect) | **Missing** (pack only under Unreal app citypacks) | N/A |

G3 work must treat these as **complementary**, not interchangeable. The worktree has the pinned contemporary source + explicit non-certification; racegps has the provisional reconstructed circuit pack + provenance narrative.

---

## 3. Source register

### A. In-repo / on-disk (OBSERVED)

| ID | Artifact | Location | Role | Confidence for 2006 certified line |
|---|---|---|---|---|
| S1 | Track provenance doc | `racegps/docs/CLEVELAND_TRACK_PROVENANCE.md` | Era table; OSM reconstruction method; length delta; source URL list | Narrative only — documents reconstruction limits |
| S2 | Demo / pack contract | `racegps/docs/CLEVELAND_DEMO.md` | Pack file roles; explicitly not 1982; M5–M9 unfinished | Product scope, not geometry certification |
| S3 | Pack `cleveland_burke_gp_1997` | `racegps/apps/unreal-akron-beta/citypacks/cleveland/burke_gp_1997/` | XODR, racing_line (410 samples), checkpoints (12 gates), metadata, dressing | **Provisional diagnostic course** — reconstructed |
| S4 | Circuit builder | `racegps/scripts/build_cleveland_circuit.py` | Filleted OSM runway/taxiway centerline → XODR/JSON; target 3389 m | Method = reconstruction; script header admits no official polyline |
| S5 | Pytest invariants | `racegps/tests/test_cleveland_circuit.py` | Closed loop, 10 turns, length ≤5% of 3389 m | Self-consistency vs published official length — **not** historical georegistration |
| S6 | Pinned OSM snapshot | worktree `data/sources/cleveland-burke/snapshot.osm` | Contemporary BKL bbox context; SHA-256 `66f90dc05b4c78238f61cbac46d49f14932c1c912b468647908523354028932b`; retrieved 2026-09-07; 22396 nodes / 2969 ways | **Contemporary only** — README forbids treating as 2006 line |
| S7 | Source record | worktree `data/sources/cleveland-burke/source.json` + README | Role string: *Contemporary context only; not the 2006 racing line* | Explicit non-certification |
| S8 | Reference contract | worktree `docs/plans/CLEVELAND_REFERENCE_CONTRACT.md` | Points to ECH, INDYCAR 2006 replay, Ohio GIS, USGS; lists still-required items | Discovery checklist — geography **not certified** |
| S9 | Readiness evidence | worktree `docs/evidence/next-five-gates/cleveland-readiness.json` | `status: failed`; no playable routes; no spawn points; `release_ready` denied | Confirms context bundle ≠ certified course |
| S10 | Large OSM extracts | `racegps/citypacks/cleveland_5.0km/*.osm` (+ buildings) | Broader contemporary city extract | Not a historic race overlay |
| S11 | Loose images | `racegps/burke_lakefront_airport.jpg`, `bud500_1.jpg` | Visual references at repo root | **Unverified** as georeferenced controls / year-tagged plans |
| S12 | Engineering/demo specs | `racegps` Cleveland showcase MD + `AGENTIC_HANDOFF_CLEVELAND.md` | Product/engineering context | Not surveyed geometry |

**Pack metrics (OBSERVED from metadata / racing_line.json)**  
- Official target: 3389 m / 2.106 mi / 10 turns / clockwise / years tagged `1997-2007`.  
- Measured haversine: **3275.82 m (−3.34%)**; OpenDRIVE planView sum cited ~3280 m in provenance.  
- Checkpoints name T1 as “Vortex (right hairpin)”; T9/T10 chicane; S/F wrap.  
- Pit lane: **metadata only** (old 1982 T1/T2 as extended pit exit) — not a second XODR road.  
- Assumptions in metadata: no official surveyed racing-line polyline; east box short of full 24R so length tracks 3389 m; lane width ~12 m vs FAA runway width; elevation flat 174 m AMSL; target speeds are control envelope, not historical lap data.

### B. Cited external sources (in provenance/metadata — not locally archived as dated plans)

| Source | Use claimed in-repo | Local archive of dated plan? |
|---|---|---|
| Wikipedia Grand Prix of Cleveland | Era lengths / T1 vortex narrative | No |
| gdecarli circuit 788 | Layout eras; 1997 remeasure; elev | No local map dump |
| Motor Sport Magazine Cleveland DB | Length / era selector | No |
| ChampCarStats Cleveland | Length eras / race list | No |
| Wikimedia SVG (Pittenger) | Pre-1990 vs later diagram | Provenance notes SVG fetch was **rate-limited 429** — **not in-repo** |
| Histor's Eye 1995 race report | Qualitative T1 / T3-T4 / T9-T10 | Narrative only; 1995 ≠ 2006 but same layout family |
| AirNav KBKL | Runway heading / endpoints | Airport ops, not race barriers |
| OSM Overpass 2026-08-22 (builder) / 2026-09-07 (worktree pin) | Pavement anchors | Contemporary aeroways |

### C. Contract-listed but still missing for G3 (MISSING)

| Need | Status |
|---|---|
| Dated **2006** (or 1997–2007 race-week) **circuit plan** with S/F, grid, temporary barriers, turn apexes | **Missing** as georeferenced controls |
| Inspection notes / timestamps from [INDYCAR 2006 full race replay](https://www.indycar.com/videos/2024/12/12-06-FullRaceReplay-Cleveland-2006) compared to plan | Link present in README/contract; **no footage inspection log / stills / control extraction in evidence** (redistribution rights not assumed) |
| Bounded OSIP / county imagery tiles for Burke + skyline with dates, CRS, hashes, terms | Catalog URLs only — **no selected tiles/hashes** |
| USGS/lidar coverage selection with vertical datum / QL | Discovery URLs only |
| Temporary race boundaries distinct from today's public aeroway/highway topology | Not separated as certified layer |
| Official surveyed racing-line / telemetry polyline | Explicitly absent (provenance + builder) |
| Independent OpenDRIVE validation (esmini/CARLA reader) on historic pack | Not evidenced for `burke_gp_1997` |
| Coherent fresh citypack sharing frame/source IDs with routes+grid+buildings+level spec | Worktree context pack: **no routes/spawns**; racegps historic pack: **not** wired to pinned `data/sources` snapshot |

---

## 4. OBSERVED vs UNVERIFIED claims

### OBSERVED (supported by files on disk)
- Pack id `cleveland_burke_gp_1997` exists with closed WGS84 racing_line, XODR, checkpoints, metadata branding guardrail.
- Measured length is within the repo's own **5%** pytest tolerance of 3389 m (−3.34%).
- Reconstruction method is OSM aeroway-based + fillets; builder docstring: *Reconstruction, not an official surveyed polyline*.
- Worktree pinned OSM is contemporary; readiness audit **failed** for release (0 routes, 0 spawns).
- G3 provisional year in handoff/production brief/reference contract is **2006**, not 1982.
- Path mismatch: tests/script expect `citypacks/cleveland/burke_gp_1997` at repo root; actual pack lives under `apps/unreal-akron-beta/citypacks/...` — root path **absent** on racegps.

### UNVERIFIED / provisional (must not be certified as historical fact yet)
- Exact 2006 start/finish, grid slots, barrier faces, cone lines, and usable racing ribbon vs full runway width.
- That east cut near taxiway E matches **2006** driven apexes (chosen to hit length target).
- T3–T10 numbering/placement vs any official 2006 turn sheet (Histor's Eye is 1995 qualitative).
- Clockwise Taxiway-G → T1-A → 06L path as the **official** centerline (plausible airport reconstruction only).
- Any claim that `burke_gp_1997` **is** the certified 2006 course (pack years string is 1997–2007 family; geometry is reconstructed).
- Root images `bud500_1.jpg` / `burke_lakefront_airport.jpg` as year-certified controls.
- Downtown street involvement (must remain **out** unless evidenced — none found).

---

## 5. G3 certification blockers (concise)

1. **No dated, georeferenced historical course plan** for 2006 (or race-week equivalent) with control points, temporary boundaries, S/F and grid — hard G3 fail per handoff §G3.2.  
2. **No corroborating view register** (replay stills / aerials) timestamped and compared to controls; INDYCAR replay is cited but not inspected into evidence.  
3. **Pinned source is contemporary OSM only** — explicitly not the 2006 line; readiness marked failed / not release_ready.  
4. **Existing `burke_gp_1997` is a provisional reconstruction** from 2026 OSM + published length, not a surveyed overlay; cannot alone pass “source-supported course.”  
5. **Tree split:** historic pack + provenance on `racegps`; pinned sources + G3 evidence scaffold on worktree — no single coherent pack sharing one source snapshot/frame/IDs.  
6. **Missing terrain/imagery acquisition package** (bounded tiles, dates, CRS, hashes, attribution).  
7. **No independent XODR reader proof** + route continuity/collision alignment evidence for a certified historic pack.  
8. **Engineering mismatch:** pytest/build expect root `citypacks/cleveland/burke_gp_1997`; that path is missing on racegps (pack only under Unreal citypacks).

**Allowed under G3 while blocked:** keep a **clearly provisional** diagnostic course; continue unrelated compiler/frame work. **Forbidden while blocked:** `release_ready: true`, “certified 2006 reconstruction,” or conflating 1982 Cleveland 500 geometry with 2006.

---

## 6. Smallest next actions (WORLD-DATA)

1. Archive a dated circuit diagram (gdecarli 2006-era map update and/or Wikimedia SVG) with checksum + license; georeference ≥4 controls to BKL pavement.  
2. Produce a stills/notes log from the official 2006 replay (no redistribution of footage required) for S/F, T1 vortex, east complex, T9/T10, grandstand side.  
3. Emit `course_controls_2006.json` (historical) separate from contemporary aeroway graph; then rebuild pack against pinned frame contract.  
4. Unify pack path: place certified outputs where build/audit expect; quarantine provisional `burke_gp_1997` as diagnostic until pass.  
5. Select bounded OSIP/USGS tiles for track+skyline only; record hashes/terms before bulk download.

---

## 7. Verdict

| Gate item | Status |
|---|---|
| Contemporary context source present | **PASS** (worktree pin) |
| Era distinction 1982 ≠ 2006 documented | **PASS** (provenance + contract + web) |
| Provisional playable/recon pack present | **PASS** (racegps `burke_gp_1997`, diagnostic) |
| Dated historical plan + georeferenced controls | **FAIL / MISSING** |
| Certified racing line for G3 | **BLOCKED** |

**G3 historical course certification: BLOCKED.**
