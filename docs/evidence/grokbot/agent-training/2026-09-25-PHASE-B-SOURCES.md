# Phase B — Cite-and-path sources (raceGPS agent training)

**Status:** Phase B cite-and-path only. **No clones, no Marketplace buys, no Unreal installs, no editor launches** until Chris greens installs.  
**Owner:** Unreal PM  
**Checked:** 2026-09-25 (America/New_York)  
**Constraint:** Gate 1 / Burke PIE stills / omni editor stay FROZEN. Prefer MIT/Apache/BSD/Epic. Anecdote ≠ API.

**Research method note:** `parallel-cli` was **not** on PATH. Used WebSearch, WebFetch, and GitHub MCP (`user-GitHub-xai`) instead. Research snapshot: [`research/2026-09-25-phase-b-research.json`](./research/2026-09-25-phase-b-research.json). Companion reject list: [`2026-09-25-PHASE-B-KILL-LIST.md`](./2026-09-25-PHASE-B-KILL-LIST.md).

---

## Summary table of keepers (ranked)

| Rank | ID | Source | License | UE / date note | Tracks | Steal | Do **not** steal |
|------|----|--------|---------|----------------|--------|-------|------------------|
| 1 | A1 | Epic — How to Set up Vehicles (Chaos) | Epic docs (EULA for engine use) | Docs serve 5.7/5.8 family; checked 2026-09-25 | 2, 3 | Plugin enable, wheel BP, torque curve, movement inputs, GameMode pawn class | Replacing raceGPS vehicle stack wholesale |
| 2 | A2 | Epic — Player Controllers | Epic docs | 5.8 doc page live 2026-09-25 | 0, 3 | Session ownership: PC persists, Pawn can die/respawn; input authority | Putting race score only on disposable Pawn |
| 3 | A2b | Epic Community — BP Getting started with Enhanced Input | Epic community tutorial | Live 2026-09-25 (slug has Epic typo `gettting`) | 0, 3 | IMC + Input Actions; Add Mapping Context on begin play | Mixing legacy Axis mappings without migration plan |
| 4 | A5 | CARLA — ASAM OpenDRIVE standalone | CARLA code MIT; docs free | Patterns only; CARLA ≠ raceGPS runtime | 1 | XODR → mesh params; junction smoothing; wall_height / additional_width | Rebuilding Cleveland in CARLA; greenfield city |
| 5 | A5b | ASAM OpenDRIVE standard (free download) | ASAM free-of-charge spec | v1.9.0 listed; checked 2026-09-25 | 1 | Road/lane/junction vocabulary for Burke XODR continuity | Treating OpenDRIVE as a full env-art pipeline |
| 6 | A4 | Internal `unreal-game-dev` skill v2.0.0 | Internal / team | No web; already installed | 0–3 | MDA, research protocol, genre-car-racing, UI, physics, build-debug | Inventing new team vocabulary outside skill |
| 7 | B1 | ChrisVifzack/unreal-simple-racer | **MIT** (LICENSE verified) | EngineAssociation **5.1**; ChaosVehiclesPlugin; last GitHub activity ~2025-05-28 | 3, 0, 2 | Checkpoint race mode, GameInstance timing, map-select widgets, PID AI *patterns* | Marketplace assets bundled in Content; city/economy |
| 8 | B2 | ScrappyCocco/UETrafficGame | **MIT** (LICENSE verified) | EngineAssociation **5.5**; ChaosVehiclesPlugin; updated ~2026-08-29 | 3, 2 | Session/round loop, Chaos vehicle playground, wiki edit notes | Full traffic-sim as Gate 1; shipping their city as Burke |
| 9 | B3 | myoozy/KinetiForge-Vehicle-System | **MIT** (LICENSE verified) | Made in **UE5.3**; active ~2026-09-20; 160+★ | 2 | Arcade/simcade *tune ideas*, async-physics discipline, modular drivetrain thinking | Replacing Chaos Vehicles stack; motorcycle claims |
| 10 | B3b | MrRobinOfficial/Unreal-NebulousVehicle | **MIT** (LICENSE.txt verified) | Chaos Vehicle *extension* plugin; checked 2026-09-25 | 2 | Thin Chaos extension patterns | Dropping raceGPS Chaos setup for this plugin |
| 11 | B3c | DanialKama/VehicularCombat | **MIT** (LICENSE verified) | EngineAssociation **5.1**; ChaosVehicles + UMG | 2, 3 | Chaos + UMG multiplayer vehicle session patterns | Combat/weapons as Gate 1 scope |
| 12 | T0-MDA | Hunicke / LeBlanc / Zubek — MDA paper (PDF) | Academic free PDF | Classic 2004; still canonical | 0 | Mechanics→Dynamics→Aesthetics; vertical slice before breadth | Using MDA as an excuse to expand scope |
| 13 | T3-UMG | Epic — Creating User Interfaces (UMG & Slate) | Epic docs | 5.8 doc hub live 2026-09-25 | 3 | Widget create → AddToViewport; HUD ownership | NullRHI “HUD works” claims |
| 14 | T1-MAP | CARLA — Maps and navigation | CARLA docs free | Waypoint/OpenDRIVE navigation patterns | 1 | Lane/waypoint mental model for arcade ribbon read | NavMesh-only AI as the racing line |
| 15 | T1-OSM | CARLA — Generate maps with OpenStreetMap | CARLA docs free | Osm2Odr → XODR → ingest | 1 | Cite OSM→XODR conversion *pattern* only | Workshop/OSM builder / two-app rgpack (explicit non-goal) |
| 16 | T1-H2O | Epic — WaterBody Python API (5.7) | Epic docs | application_version=5.7 | 1 | Water body types / surface query vocabulary for Lake Erie bar | Building a water tech demo instead of Burke skyline stills |
| 17 | ART1 | Evenant — Painting Environment Concepts In No Time | Free web article | Dated 2024-02-24; checked 2026-09-25 | 0, 1 | 4-value thumbnails; value hierarchy for skyline/water/track | Style drift away from Midnight Club / Burke bar |
| 18 | C-R1 | Reddit — chaos vehicle arcade racing | Anecdote (lead only) | Thread 2024; checked 2026-09-25 | 2 | “Arcade settings exist but need custom forces”; mass/COM tips | Treating comments as Chaos API truth |
| 19 | C-R2 | Reddit — Chaos Vehicle Arcade Settings | Anecdote (lead only) | 2022; sparse docs complaint | 2 | Lower mass, raise friction, reduce spring — *hypotheses to test* | Copying Marketplace plugin recommendations blindly |
| 20 | C-R3 | Reddit — viewport pause when unfocused | Anecdote (lead only) | Editor CPU throttle ≠ packaged exit | 3 | Distinguish editor background throttle vs real ViewportClosed | Unlocking Gate 1 on void/black screen |
| 21 | C-R4 | Reddit — performance when Game window not in focus | Anecdote (lead only) | Standalone vs New Editor Window | 3 | Focus / tick-rate failure-mode checklist | Assuming `-game` auto-stays focused |
| 22 | C-F1 | UE Forums — packaged game instantly quits | Anecdote (lead only) | Maps & Modes / -log / static init | 3 | Default map + Development `-log` before Shipping | Shipping silent quit as “viewport survival PASS” |

---

## Track 0 — Prototyper + Unreal PM (meta)

### 0.1 MDA / core loop
| Field | Value |
|-------|-------|
| **Title** | MDA: A Formal Approach to Game Design and Game Research |
| **URL** | https://users.cs.northwestern.edu/~hunicke/MDA.pdf |
| **License** | Academic free PDF (cite authors: Hunicke, LeBlanc, Zubek) |
| **Date checked** | 2026-09-25 |
| **UE version** | N/A |
| **Steal** | Map countdown→racing→finish HUD→R restart onto Mechanics/Dynamics/Aesthetics; vertical slice before Workshop/OSM breadth |
| **Do not** | Expand Gate 1 into economy/city-gen because MDA mentions “aesthetics” |
| **Safety** | Open academic source |

### 0.2 Research protocol + session ownership
| Field | Value |
|-------|-------|
| **Title** | Player Controllers in Unreal Engine |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/player-controllers-in-unreal-engine |
| **License** | Epic documentation |
| **Date checked** | 2026-09-25 |
| **UE version** | Doc page labels 5.8; concepts apply to 5.7 raceGPS target |
| **Steal** | PC as timing/input authority; Pawn transient; score/restart on durable objects |
| **Do not** | API copy-paste from mismatched tutorial versions without local verify |
| **Safety** | Official Epic |

| Field | Value |
|-------|-------|
| **Title** | BP Getting started with Enhanced Input (Epic Community) |
| **URL** | https://dev.epicgames.com/community/learning/tutorials/1w4K/unreal-engine-bp-gettting-started-with-enhanced-input |
| **License** | Epic community learning |
| **Date checked** | 2026-09-25 |
| **UE version** | UE5 Enhanced Input (default since ~5.1) |
| **Steal** | Input Action + Mapping Context workflow; Add Mapping Context on possess/begin play |
| **Do not** | Leave legacy Action/Axis live without an explicit migration note |
| **Safety** | Official Epic community; note Epic’s own `gettting` slug typo |

### 0.3 Evidence gates (internal)
| Field | Value |
|-------|-------|
| **Title** | `unreal-game-dev` skill v2.0.0 — `references/research-protocol.md`, `build-debug-test.md`, `genre-car-racing.md` |
| **URL** | *(internal — no web)* |
| **License** | Team internal |
| **Date checked** | 2026-09-25 |
| **Steal** | UE version first (5.7); compile ≠ playable; NullRHI/black void = FAIL |
| **Do not** | Treat skill text as a substitute for Epic API pages when versions diverge |

### 0.4 Digital art literacy (PM judgment)
See **Cross-cutting digital art** below (Evenant thumbnails). Enough to *judge* Burke stills (silhouette, water/skyline horizon), not to replace CA.

---

## Track 1 — Course Architect

### 1.1–1.2 OpenDRIVE / street continuity (patterns only)
| Field | Value |
|-------|-------|
| **Title** | CARLA — ASAM OpenDRIVE standalone mode |
| **URL** | https://carla.readthedocs.io/en/latest/adv_opendrive/ |
| **License** | Docs free; CARLA simulator code MIT (https://github.com/carla-simulator/carla) |
| **Date checked** | 2026-09-25 |
| **UE version** | CARLA’s own UE fork — **pattern cite only**, not a raceGPS dependency |
| **Steal** | `generate_opendrive_world` parameter meanings (vertex_distance, smooth_junctions, wall_height); XODR quality gates at junctions |
| **Do not** | Rebuild Cleveland in CARLA; swap raceGPS mesh pipeline for CARLA standalone void roads |
| **Safety** | Open docs; do not clone CARLA until Chris greens |

| Field | Value |
|-------|-------|
| **Title** | ASAM OpenDRIVE® (official free specification) |
| **URL** | https://www.asam.net/standards/detail/opendrive |
| **License** | ASAM: download of the standard is free of charge (per ASAM page) |
| **Date checked** | 2026-09-25 |
| **UE version** | N/A (road network XML `.xodr`) |
| **Steal** | Reference-line / lane / junction vocabulary for shared `cleveland_burke_gp_1997_ez` XODR |
| **Do not** | Turn course work into an ADAS validation project |
| **Safety** | Standards body; free download |

| Field | Value |
|-------|-------|
| **Title** | CARLA — Maps and navigation |
| **URL** | https://carla.readthedocs.io/en/latest/core_map/ |
| **License** | Free docs |
| **Date checked** | 2026-09-25 |
| **Steal** | OpenDRIVE-backed waypoints as a *racing-line thinking aid* |
| **Do not** | Assume CARLA Waypoint API exists inside raceGPS |

| Field | Value |
|-------|-------|
| **Title** | CARLA — Generate maps with OpenStreetMap |
| **URL** | https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/ |
| **License** | Free docs; OSM data ODbL (separate) |
| **Date checked** | 2026-09-25 |
| **Steal** | Osm2Odr → XODR conversion *pattern* citation |
| **Do not** | Two-app rgpack / Workshop / OSM builder (outline non-goal) |

### 1.3 Water + skyline env vocabulary
| Field | Value |
|-------|-------|
| **Title** | unreal.WaterBody — Unreal Python 5.7 |
| **URL** | https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/WaterBody.html?application_version=5.7 |
| **License** | Epic docs |
| **Date checked** | 2026-09-25 |
| **UE version** | Explicit **5.7** |
| **Steal** | Water body type vocabulary for Lake Erie / shoreline read in stills |
| **Do not** | Water tech rabbit hole before CLEVELAND_VISUAL_BAR stills PASS |
| **Safety** | Official; some narrative Water System pages 403’d from this environment — API page verified |

### 1.4 Course versioning mindset
Reuse in-tree Burke / Cleveland pipelines (Tier A3 from outline) — wrap/light, don’t rebuild. No new public URL required; cite project evidence paths when specialists write Phase C packs.

---

## Track 2 — Vehicle Arcade

### 2.1 Official Chaos Vehicles
| Field | Value |
|-------|-------|
| **Title** | How to Set up Vehicles in Unreal Engine |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/how-to-set-up-vehicles-in-unreal-engine |
| **License** | Epic docs |
| **Date checked** | 2026-09-25 |
| **UE version** | Page serves current 5.x docs (labeled 5.8 in fetch); prefer matching **5.7** project |
| **Steal** | ChaosVehiclesPlugin enable; ChaosVehicleWheel; torque curve; Wheel Setups bone names; throttle/steer/brake/handbrake inputs; GameMode Default Pawn |
| **Do not** | PhysX Vehicles plugin path; motorcycle setups; Marketplace vehicle packs without Chris OK |
| **Safety** | Official Epic |

| Field | Value |
|-------|-------|
| **Title** | UChaosVehicleMovementComponent (API) |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosVehicles/UChaosVehicleMovementComponent |
| **License** | Epic API docs |
| **Date checked** | 2026-09-25 |
| **UE version** | 5.7-family API pages also exist for Python (`ChaosVehicleMovementComponent`) |
| **Steal** | Arcade-oriented config names (TorqueControl, StabilizeControl, thrusters/aerofoils as *optional*) — read before Reddit folklore |
| **Do not** | Assume every property is documented with arcade examples (community repeatedly says docs are sparse) |

### 2.2 Open Chaos / arcade spikes (Tier B3)
| Field | Value |
|-------|-------|
| **Title** | myoozy/KinetiForge-Vehicle-System |
| **URL** | https://github.com/myoozy/KinetiForge-Vehicle-System |
| **License** | **MIT** |
| **Date checked** | 2026-09-25 (README + LICENSE; activity ~2026-09-20) |
| **UE version** | Author: made in **UE5.3**; async physics required |
| **Steal** | Tuning philosophy (input smoothing, LSD lock ratio feel); modular component thinking |
| **Do not** | Replace Epic Chaos Vehicles with KinetiForge for Gate 1; do not clone until Chris greens |
| **Safety** | MIT; custom physics ≠ drop-in Chaos replacement — pattern class only |

| Field | Value |
|-------|-------|
| **Title** | MrRobinOfficial/Unreal-NebulousVehicle |
| **URL** | https://github.com/MrRobinOfficial/Unreal-NebulousVehicle |
| **License** | **MIT** |
| **Date checked** | 2026-09-25 |
| **UE version** | Chaos Vehicle extension plugin (verify locally before any future install) |
| **Steal** | How a thin plugin wraps Chaos rather than forking the world |
| **Do not** | WIP features as production truth |

| Field | Value |
|-------|-------|
| **Title** | DanialKama/VehicularCombat |
| **URL** | https://github.com/DanialKama/VehicularCombat |
| **License** | **MIT** |
| **Date checked** | 2026-09-25 |
| **UE version** | **5.1** uproject; ChaosVehiclesPlugin enabled; PhysXVehicles disabled |
| **Steal** | Chaos wheeled pawn + UMG module dependency pattern |
| **Do not** | Combat loop / Steam online subsystem as Gate 1 |

### 2.3 Community leads (anecdote ≠ API)
| Field | Value |
|-------|-------|
| **Title** | r/unrealengine — chaos vehicle arcade racing |
| **URL** | https://www.reddit.com/r/unrealengine/comments/1aco1jp/chaos_vehicle_arcade_racing/ |
| **License** | Reddit user content; lead only |
| **Date checked** | 2026-09-25 |
| **Steal** | Failure modes: Chaos can be overkill for kart; arcade settings exist but need fiddling / custom forces |
| **Do not** | Ship “Reddit said skip Chaos” without raceGPS Chaos already chosen |

| Field | Value |
|-------|-------|
| **Title** | r/unrealengine — Chaos Vehicle Arcade Settings |
| **URL** | https://www.reddit.com/r/unrealengine/comments/xj3977/chaos_vehicle_arcade_settings/ |
| **License** | Lead only |
| **Date checked** | 2026-09-25 |
| **Steal** | Hypotheses: reduce mass, lower COM, raise wheel friction, soften springs — **then measure in-project** |
| **Do not** | Pay Marketplace “Advanced Vehicle System” suggestions from thread (see kill list) |

**R-Tune class note:** Pattern class from outline maps to **paid** Fab product “R-Tune Vehicle Physics 2.0 Pro” — see kill list. Prefer open **KinetiForge** as the free B3 stand-in.

---

## Track 3 — Race Systems

### 3.1 Session loop + HUD open patterns (Tier B1/B2)
| Field | Value |
|-------|-------|
| **Title** | ChrisVifzack/unreal-simple-racer |
| **URL** | https://github.com/ChrisVifzack/unreal-simple-racer |
| **License** | **MIT** (code). README: *assets from Marketplace* — do **not** redistribute those assets. |
| **Date checked** | 2026-09-25 |
| **UE version** | **5.1**; ChaosVehiclesPlugin + RacingAI plugin |
| **Steal** | Checkpoint race GameMode; lap time on GameInstance; map selection widgets; PID spline-follow AI *ideas* (defer AI until loop+visuals green) |
| **Do not** | City generation; Marketplace content reuse; Behavior Tree complexity before Gate 1 |
| **Safety** | MIT code OK to study after green; verify asset licenses separately before any content copy |

| Field | Value |
|-------|-------|
| **Title** | ScrappyCocco/UETrafficGame |
| **URL** | https://github.com/ScrappyCocco/UETrafficGame |
| **License** | **MIT** code; README claims CC0 for listed third-party assets (see repo `ASSETS.md`) |
| **Date checked** | 2026-09-25 |
| **UE version** | **5.5** uproject; ChaosVehiclesPlugin; wiki: https://github.com/ScrappyCocco/UETrafficGame/wiki |
| **Steal** | Round/session structure, Chaos vehicle playground habits, “inspired by Epic Vehicle template” orientation |
| **Do not** | Promote traffic replay puzzle to Gate 1; adopt their large map as Cleveland |
| **Safety** | MIT; still no clone until Chris greens |

### 3.2 UMG race HUD
| Field | Value |
|-------|-------|
| **Title** | Creating User Interfaces With UMG and Slate |
| **URL** | https://dev.epicgames.com/documentation/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine |
| **License** | Epic docs |
| **Date checked** | 2026-09-25 |
| **Steal** | Widget lifecycle; UI tools overview for checkpoint + finish screens |
| **Do not** | Claim HUD PASS under NullRHI / black void |

### 3.3 Viewport / packaged `-game` survival (leads only)
| Field | Value |
|-------|-------|
| **Title** | r/unrealengine — Which setting causes the viewport to pause when clicking off of it? |
| **URL** | https://www.reddit.com/r/unrealengine/comments/1dpewlt/which_setting_causes_the_viewport_to_pause_when/ |
| **License** | Lead only |
| **Date checked** | 2026-09-25 |
| **Steal** | Editor “Use Less CPU when in Background” mental model — **editor ≠ packaged** |
| **Do not** | Equate editor pause with raceGPS ViewportClosed FAIL evidence |

| Field | Value |
|-------|-------|
| **Title** | r/unrealengine — Performance issues when "Game" window is not in focus |
| **URL** | https://www.reddit.com/r/unrealengine/comments/tqf9kj/performance_issues_when_game_window_is_not_in/ |
| **License** | Lead only |
| **Date checked** | 2026-09-25 |
| **Steal** | Standalone Game vs New Editor Window focus differences |
| **Do not** | Treat tick-rate anecdotes as API |

| Field | Value |
|-------|-------|
| **Title** | Epic Forums — Why does my packaged game instantly quit? |
| **URL** | https://forums.unrealengine.com/t/why-does-my-packaged-game-instantly-quit/277996 |
| **License** | Forum anecdote |
| **Date checked** | 2026-09-25 |
| **Steal** | Check Game Default Map; run Development with `-log`; don’t debug Shipping first |
| **Do not** | Mark Gate 1 unlocked because a different project’s quit was “just default map” |

---

## Cross-cutting — digital art / composition (PM + CA still judgment)

| Field | Value |
|-------|-------|
| **Title** | Evenant — Painting Environment Concepts In No Time (thumbnailing / 4 values) |
| **URL** | https://www.evenant.com/articles/painting-environment-concepts-in-no-time |
| **License** | Free public article (Evenant site) |
| **Date checked** | 2026-09-25 |
| **Steal** | Fast value thumbnails; hero focal; diagonals for motion; sky vs near-dark hierarchy — maps to Burke EZ ribbon + skyline + Lake Erie readability |
| **Do not** | Paint a new fantasy city; abandon Midnight Club / Cleveland visual bar |
| **Safety** | Free learning; no asset piracy |

| Field | Value |
|-------|-------|
| **Title** | MDA PDF (also Track 0) — aesthetics literacy for “what good feels like” |
| **URL** | https://users.cs.northwestern.edu/~hunicke/MDA.pdf |
| **Steal** | Name the aesthetic target (arcade street thrill) before dressing the track |

**Note:** A LeMoore College OER digital-art PDF appeared in search results but was not successfully verified in this pass — **omitted** (zero fabricated/unverified URLs).

---

## Phase C recommendation — study first when unlocked

Specialists should read these **3–5** before writing `*-training/` one-pagers (still **no clones** until Chris greens installs):

1. **Epic Chaos vehicle setup** — https://dev.epicgames.com/documentation/unreal-engine/how-to-set-up-vehicles-in-unreal-engine *(VA + RS)*  
2. **Epic Player Controllers + Enhanced Input community tutorial** — PC persistence + IMC *(PM + RS)*  
3. **CARLA OpenDRIVE standalone + ASAM OpenDRIVE page** — XODR pattern literacy *(CA)* — https://carla.readthedocs.io/en/latest/adv_opendrive/ + https://www.asam.net/standards/detail/opendrive  
4. **ChrisVifzack/unreal-simple-racer README + LICENSE** (cite-and-path) — countdown/checkpoint/restart patterns *(RS)* — https://github.com/ChrisVifzack/unreal-simple-racer  
5. **ScrappyCocco/UETrafficGame README + wiki** (cite-and-path) — Chaos session playground *(RS + VA)* — https://github.com/ScrappyCocco/UETrafficGame  

Optional sixth for VA arcade feel (patterns only): **KinetiForge** README — https://github.com/myoozy/KinetiForge-Vehicle-System  

Internal always-on: `unreal-game-dev` research-protocol + genre-car-racing.

---

## Sources appendix (every URL cited above)

### Epic / official
- https://dev.epicgames.com/documentation/unreal-engine/how-to-set-up-vehicles-in-unreal-engine  
- https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/ChaosVehicles/UChaosVehicleMovementComponent  
- https://dev.epicgames.com/documentation/unreal-engine/player-controllers-in-unreal-engine  
- https://dev.epicgames.com/community/learning/tutorials/1w4K/unreal-engine-bp-gettting-started-with-enhanced-input  
- https://dev.epicgames.com/documentation/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine  
- https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/WaterBody.html?application_version=5.7  

### CARLA / ASAM
- https://carla.readthedocs.io/en/latest/adv_opendrive/  
- https://carla.readthedocs.io/en/latest/core_map/  
- https://carla.readthedocs.io/en/latest/tuto_G_openstreetmap/  
- https://github.com/carla-simulator/carla  
- https://www.asam.net/standards/detail/opendrive  

### GitHub keepers (MIT verified 2026-09-25)
- https://github.com/ChrisVifzack/unreal-simple-racer  
- https://github.com/ScrappyCocco/UETrafficGame  
- https://github.com/ScrappyCocco/UETrafficGame/wiki  
- https://github.com/myoozy/KinetiForge-Vehicle-System  
- https://github.com/MrRobinOfficial/Unreal-NebulousVehicle  
- https://github.com/DanialKama/VehicularCombat  

### Theory / art
- https://users.cs.northwestern.edu/~hunicke/MDA.pdf  
- https://www.evenant.com/articles/painting-environment-concepts-in-no-time  

### Community leads only
- https://www.reddit.com/r/unrealengine/comments/1aco1jp/chaos_vehicle_arcade_racing/  
- https://www.reddit.com/r/unrealengine/comments/xj3977/chaos_vehicle_arcade_settings/  
- https://www.reddit.com/r/unrealengine/comments/1dpewlt/which_setting_causes_the_viewport_to_pause_when/  
- https://www.reddit.com/r/unrealengine/comments/tqf9kj/performance_issues_when_game_window_is_not_in/  
- https://forums.unrealengine.com/t/why-does-my-packaged-game-instantly-quit/277996  

### Rejects
See [`2026-09-25-PHASE-B-KILL-LIST.md`](./2026-09-25-PHASE-B-KILL-LIST.md).

---

**Keeper count (table rows with real URLs + license/date notes):** 22 listed (16 primary keepers + 6 community leads).  
**Next gate:** Chris greens Phase C study packs and/or any future clone/install list.
