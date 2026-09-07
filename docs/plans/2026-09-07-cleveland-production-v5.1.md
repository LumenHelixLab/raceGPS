# raceGPS — Cleveland Production Brief and Completion Plan

Lumen Helix Solutions · LumenHelix.com
Prepared for C. G. Phillips / Raziel
Document version: **5.1** · Date: 2026-09-07
Status: **User-approved direction; production planning updated; runtime execution not verified**

**Deliver a premium, recognizable Cleveland racing experience first: a historically grounded airport course, two physical AI opponents, convincing arcade vehicle dynamics, a geographically aligned skyline, and polished sunset, twilight and midnight environments. Finish the offline product before expanding into the online ZIP-territory championship.**

This revision supersedes the v5.0 combined offline/online release schedule, its permissive online Route Forge model, and its understated “accurate roads, styled city” visual target. The user has authorized initiative within this direction. Routine technical choices do not require another planning approval. Unverified historical details and new competitive rules remain explicitly distinguishable from user requirements.

**Locked requirements and engineering decisions**

| Topic | Current requirement |
|---|---|
| Product ambition | Premium urban arcade racing, recognizable real geography, high production value and excellent UI/UX; awards and virality are ambitions, not guaranteed outcomes |
| Beta | Cleveland historical airport racing reference; one human plus at least two physical AI opponents |
| Visual environments | Sunset, twilight and midnight, each authored and tested as a finished presentation |
| World reconstruction | Combine georeferenced roads/elevation with available photographic references, scans, reconstructed landmarks and geographically appropriate models; generic kits alone do not satisfy local identity |
| CARLA and other tools | Evaluate concrete contributions to the offline road/asset/traffic/telemetry pipeline; choose based on reproducible output, fidelity, rights, compatibility and cost |
| Offline | Remains on the previously agreed offline path; it does not acquire online ZIP ownership or route-selection restrictions |
| Online input | Player supplies ZIP; system resolves geography and devises the competitive map/course |
| Online uniqueness | One persistent registered map per ZIP; no requester-selected route and no reroll |
| Online ownership | Must be won in verified competition, including by the person who first requested the map |
| Execution order | Cleveland demo → complete offline beta/release → ZIP generation proof → closed championship → supported expansion |

**Evidence carried forward**

The selected-source audit observed repository commit [b56b6c814c23423d13b7683607d0da5ba89130f2](https://github.com/LumenHelixLab/raceGPS/commit/b56b6c814c23423d13b7683607d0da5ba89130f2). It found a declared UE 5.7 project, Akron and Cleveland map files, conflicting completion documentation, backend-only connectivity smoke tests and a release workflow that publishes a tools archive rather than retained game artifacts. Build.bat does invoke cooking, but execution was not verified. The inspected ghost uses collision-free transform following, which cannot establish physical AI racing. Protocol parsing checks an object/type before a TypeScript cast and needs fuller validation before public networking.

These findings are a prior selected-source review, not a fresh full audit or proof of failure at runtime. Refresh head and reproduce before editing. Do not downgrade to UE 5.5 merely because the August attachment recommends it. No Unreal build host, editor, game executable or access to the user's local D:\projects checkout has been verified in this session.

**Why Cleveland is the first production case**

The [Encyclopedia of Cleveland History](https://case.edu/ech/articles/g/grand-prix-cleveland) identifies the race's original Budweiser-Cleveland 500 name and Burke Lakefront Airport setting. INDYCAR publishes an [official 2006 Cleveland race replay](https://www.indycar.com/videos/2024/12/12-06-FullRaceReplay-Cleveland-2006), providing a useful visual reference source. Availability of a reference does not grant redistribution rights to its footage.

The production advantage is a bounded competitive space with opportunities to demonstrate speed, braking, overtaking and skyline presentation. This is an engineering inference from the airport-course setting. It does not establish that the current Cleveland map contains the correct historical circuit.

Use the **2006 event as the provisional reference package**, because an official replay is available. Verify the layout using a dated circuit plan and additional independent evidence before finalizing geometry. Do not label it a reconstruction of the original 1982 course without verifying that year's layout. Course dimensions, turn numbering, temporary barriers and start/finish placement remain research items until checked.

Production choice: historically grounded circuit geometry with a **contemporary, source-dated Cleveland environment** and fictional raceGPS evening event dressing. This avoids accidentally claiming a period-perfect recreation while mixing modern buildings with a historical track. Record deliberate changes. Historical sponsor liveries and event signage are not necessary to make the location recognizable.

**The player-facing demo**

1. Launch into a clean raceGPS title/menu scene with a recognizable Cleveland establishing view.
2. Select the finished demo car's permitted handling/difficulty configuration and Sunset, Twilight or Midnight.
3. See a compact course preview, controls and opponent information; enter the grid without a developer console.
4. Race a short multi-lap event against two physical opponents, with braking, passing, collision response and recovery all usable.
5. Receive correct placement/time/penalties; watch a short replay or save a local highlight; rematch or return to the garage/menu.

Keep the first playable race focused. Do not make demo completion depend on online identity, a giant garage catalog, weather simulation or dynamic global time. Extend the established demo into the offline product after acceptance.

**Reconstruction and art pipeline**

| Layer | Source and method | Acceptance |
|---|---|---|
| Race surface | Sourced course control points over current geospatial pavement/terrain data; reviewed overlay for temporary circuit boundaries | Correct scale, topology, surface continuity, starting space and checkpoint reachability |
| Local environment | Available imagery/elevation/scans, measured footprints and specifically modeled important structures | Geography and proportions agree with documented references; uncertain measurements marked |
| Skyline | Geolocated silhouettes and representative facade/material detail at the distances seen from the circuit | Correct landmark ordering, bearing, relative height and parallax from at least three track viewpoints |
| Foreground | Detailed pavement, markings, joints, barriers, lighting, vehicles and trackside objects | Credible close-range appearance, collision and material response without repeated obvious placeholders |
| Supporting structures | Curated high-quality assets fitted to actual architectural context | Correct dimensions/style/materials; no substitution that destroys the location's identity |
| Event treatment | raceGPS barriers, signage, portable lighting and presentation elements | Clearly a creative treatment; follows gameplay visibility and performance constraints |

Maintain a reference register: feature, source/date, coordinate frame, measured or estimated dimensions, confidence, intended modification and reviewer. GPS/OSM positioning does not by itself supply visual appearance. Photographic reconstruction is bounded by actual source coverage.

Use screen-space error and player sightlines to allocate detail. Give the race surface, car and near barriers the highest fidelity; use optimized geometry/materials for the skyline while retaining real placement. Test moving-camera parallax before accepting distant scenery. Do not copy a flat skyline image onto a nearby plane and call it geographic reconstruction.

Evaluate CARLA against a specific need: road-format comparison, a usable asset export, traffic behavior reference or telemetry scenario. For every external tool, obtain one working import in the pinned Unreal build and compare it with the existing method. No tool receives credit from its name, marketing screenshots or a proposed adapter alone.

**Three lighting environments, one reproducible world**

| Preset | Visual direction | Gameplay/engineering checks |
|---|---|---|
| Sunset | Warm low-angle sunlight, long shadows, lake highlights, readable skyline | Glare at actual braking points, shadow aliasing, visibility when heading toward the sun, stable exposure |
| Twilight | Cool ambient sky, warmer practical lights, gradual separation of car and background | Preserve road markings and opponent silhouette; window/headlight balance; avoid an exposure-dependent invisible road |
| Midnight | Dark sky with believable event illumination, headlights, taillights and selectively lit skyline | Headlights reveal the braking distance needed at supported speed; barriers/checkpoints remain legible; dynamic-light cost stays within budget |

Choose and record a geographic location, date and sun orientation for the reference lighting setup. Sunset is not placed arbitrarily behind the skyline in every direction. Artistic adjustments are documented. The three presets initially keep geometry, dry-surface physics and race rules fixed so lighting can be evaluated independently.

Do not imply these exact evening conditions recreate a particular historical race. Dynamic sunset-to-midnight progression and wet-weather handling are later enhancements. Wet-looking materials must not silently communicate a grip level different from the simulated surface.

**Physics and AI proof**

The airport demo must demonstrate acceleration, braking, turning, drift recovery, suspension response over representative seams, wheel contact, car-to-car contact, barrier impacts, overtaking, off-course reset and correct lap/finish logic. Record speed/steering/throttle/brake, slip metrics where available, collisions, AI state/recovery events, frame time and race events.

Two physical opponents use steering, throttle and brakes, with bounded racing-line choices, collision avoidance and explicit stuck recovery. Replay ghosts remain a separate non-colliding feature. AI must not gain invisible speed advantages or teleport to compensate for a weak controller during a normal race. Any catch-up assistance is disclosed and disabled in benchmark runs.

Use a 20-run baseline per accepted demo configuration, requiring each opponent to finish at least 19 times. Additional obstruction tests must recover or terminate in an explicit DNF rather than stall the event. Fixed seeds help compare scenarios but do not prove cross-machine bitwise physics determinism.

**One additional validation area**

A flat, open airport course cannot certify dense-city behavior. Reuse a small existing Akron segment as an internal diagnostic fixture containing a tight intersection, building occlusion, an elevation/grade transition and a streaming boundary where feasible. This fixture is not a second polished demo or a new player-facing mode.

Pass collision continuity, camera occlusion, road matching and fast traversal there before claiming the pipeline is ready for Akron or ZIP territories. This catches design mistakes early while keeping the public demo focused.

**UI/UX and shareability acceptance**

- One consistent visual language across title/menu, garage preview, course preview, countdown, HUD, pause, results and replay.
- Controller focus, remapping, dead zones, scalable text, audio controls and reduced flash/motion work from the first public demo.
- HUD emphasizes actionable race information without cluttering the skyline or braking zones. Route cues do not rely on color alone.
- Input-to-response, camera movement and frame pacing are evaluated as part of handling quality.
- Replays use recorded state and authored cameras with collision/occlusion checks. Include a clean HUD-free view and crop-safe framing for portrait capture where feasible.
- Highlight saving is local and user-initiated. No automatic social posting, artificial engagement metrics or claim of guaranteed virality.
- External players must recognize the setting from matched reference viewpoints and complete the first race without developer help.

**Revised near-term sprint sequence**

Two-week sprints are planning units. Estimates require a working Unreal host, named owners and actual throughput. The previous combined 32–40-week promise is withdrawn as a forecast for the revised online scope. Four demo sprints are an initial allocation, not an eight-week guarantee of premium completion.

| Sprint | Work | Required evidence |
|---|---|---|
| **D1 — Baseline and geographic proof** | Refresh source; reproduce build path; inventory real assets; assemble dated Cleveland reference package; identify circuit overlay and skyline viewpoints; verify host and toolchain | Current-state register, build logs or precise blockers, source/provenance map, declared course uncertainties and hardware profile |
| **D2 — Playable surface and visual benchmark** | Valid course collision and one finished car; packaged solo race; representative course segment with skyline and three lighting presets; minimum menu/HUD/results | Actual packaged drive plus fixed-view reference comparisons and frame-time captures for all presets |
| **D3 — Race and physics quality** | Two physical rivals, overtaking/recovery, contact and penalties, complete race flow, controller/accessibility; internal urban diagnostic fixture | AI reliability runs, physics-event logs, keyboard/controller playthroughs and diagnostic traversal evidence |
| **D4 — Premium demo candidate** | Finish visible course art/audio/FX/UI, replay/highlight, optimize, install/update smoke, external playtest and fixes | Installable artifact, independent-machine run, accepted three-condition visual suite, performance report and resolved blocker list |

If D2 cannot meet the visual benchmark, resolve the asset/reconstruction/lighting pipeline before scaling scenery. If D3 fails physics or AI reliability, do not compensate with a trailer. D4 closes only with an actual accepted game build.

After the demo, retain the offline work from v5.0: CityPack v2 and coordinate/hash contracts; bounded Akron cruise area and curated routes; three garageGPS vehicle definitions with controlled parts/presets; offline Route Forge/ghost/progression where already in scope; complete accessibility; install/update/save migrations; independent beta and supported release. Re-estimate that work using demonstrated content and integration throughput.

**Online program, preserved separately**

US ZIP resolution → canonical territory record → cached road/elevation snapshot → system-generated candidates → hard validity filters → competitive-quality evaluation → deterministic course selection → physical/visual certification → one published map.

The user chooses the ZIP, not the course. A unique country/ZIP key reserves generation before work starts; duplicate requests reuse the job or published record. ZIPs with no supported geographic resolution or acceptable course produce an explicit unsupported/pending result, not a fabricated location. Repair versions retain the same territory identity and history; no repeat creation or reroll is available.

The requester has no automatic ownership. A verified competition awards ownership and later verified results can transfer it. Keep requester attribution separate from current champion. Standardized championship vehicle specifications, equal conditions/practice, rotated-grid multi-heat events, inactivity rules and defense windows are engineering proposals requiring balancing; they are not all user-confirmed rules yet.

Before broad rollout, pilot a small set covering dense urban, suburban, rural, hilly and difficult boundaries. Measure course viability, requester manipulation resistance, start-position bias, passing opportunities, completion, source coverage, recognizable reconstruction quality, build cost, install size and frame budget. Equal race duration does not by itself establish fairness. Separate per-map competition from cross-map reward balancing.

Historic showcase courses are a curated offline content family. ZIP championship maps are system-selected online territories. They can share the compiler, materials, vehicles and validation tools without sharing ownership or route-selection rules. A historical course does not automatically become the championship map of whichever ZIP contains its start line.

**Future city selection**

Use historical racing locations as candidates, but select the second showcase only after Cleveland is accepted. Score source availability and rights, manageable course extent, recognizable scenery, source coverage, new engineering coverage and production effort. Prefer a next course that tests a missing capability—such as narrow urban streets or elevation—while reusing proven components. Do not begin a multi-city art backlog before the first city's quality/cost is known.

**Acceptance and evidence contract**

Every delivery records source commit, engine/runtime/plugin versions, assets/provenance, target hardware, commands/logs, test results, artifact checksums, video and limitations. Distinguish source present, editor verified, packaged verified and independent-user verified. Do not use historical checked boxes or passing portable tests to claim a working Unreal game.

Proposed demo targets: recommended machine at 1080p with median frame time ≤16.7 ms and p95 ≤20 ms on fixed representative runs; report p99 and worst streaming stalls. Declare minimum hardware only after measurement. First usable drive within 60 seconds of ordinary launch, with first-ever shader work measured separately. Test all three lighting presets, both input methods, reduced effects and the independent installer path. At least 8/10 external testers should complete a first race without assistance; repeated visibility/handling complaints block premium acceptance even if averages pass.

The primary next execution task is **D1: reproduce the current Unreal baseline and assemble the circuit/reference contract**. This document completes the updated production brief. No compile, playable map inspection, package, local-machine connection or implementation success is claimed by this planning update.
