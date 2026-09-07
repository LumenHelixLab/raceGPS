# D1 execution checkpoint — Cleveland production foundation

Lumen Helix Solutions · 2026-09-07

**Portable verification passed. World-data and Unreal execution gates remain open.**

Base: `b56b6c814c23423d13b7683607d0da5ba89130f2`. Work branch:
`codex/d1-cleveland-build-baseline`. The approved direction is recorded in
[the v5.1 production plan](2026-09-07-cleveland-production-v5.1.md).

This checkpoint implements build/onboarding corrections, runs actual checks,
and records content inventory. It is not a playable-demo completion claim.

## Executed evidence

Host: Linux x86_64; Python 3.12.13; Node 24.19.0; npm 11.9.0.

| Check | Result | Limit |
|---|---|---|
| Clean npm dependency install from lockfile | Pass | Installed using `--ignore-scripts`; no native game/toolchain validation |
| Baseline Python after installing missing jsonschema | 205 passed, 5 skipped | Initial declared dependency install could not collect the suite |
| Final Python suite | **214 passed, 5 skipped** | Includes 9 new orchestration tests using fake tools; not Unreal tests |
| TypeScript typecheck | Pass | Static types do not establish runtime protocol validation |
| TypeScript workspace build | Pass | Compiles backend/reference packages, not Unreal |
| Backend tests | **5 passed** | Room utilities and HTTP health/rooms only; no replicated Unreal race |
| Real Akron citypack validator | **FAIL: 1 error, 34 warnings** | Disconnected graph; review actual geometry before deciding repairs |
| Unreal preflight on this host | **FAIL: Unreal 5.7 unavailable** | No compile, editor load, package or playtest executed |

Evidence lives in [docs/evidence/d1](../evidence/d1/). The five Python skips require
`akron_raw.osm`, which is absent from this checkout. They are not counted as passing.
Many existing tests inspect source text or fixtures; their count does not certify
the real-world geometry or a polished game. Frozen Python package versions accompany
this run as evidence, not a newly declared production dependency policy.

## Implemented changes

- One Python build/cook/archive implementation, with the existing Build.bat as a
  compatibility entry point. Remove malformed UBT path construction and silent
  UE 5.5 fallback. Validate engine major/minor from Build.version.
- Build the editor first and explicitly build the game during UAT BuildCookRun.
  Preserve exit codes/logs and stop after a failed step.
- Fresh archive directories prevent stale files being mistaken for output of a
  successful build. Windows package checks require a game executable and cooked
  content. Evidence records commands, source state, engine metadata and SHA-256s.
  Success is labeled `packaged_not_play_tested`.
- Stage citypack data and level specs under the packaged project; adjust the
  importer to resolve those locations when running cooked data. Editor paths remain
  repository-relative. **The C++ change is not compiled on this host.**
- Unreal CI is an explicit operator-dispatched gate on a labeled, provisioned
  Windows runner. It retains game/evidence artifacts and does not publish releases.
  A public PR is not automatically run on that trusted host.
- Declare jsonschema in requirements-dev.txt, used by portable CI. Build local
  protocol/race-engine packages before backend dev/test/typecheck/build and declare
  the backend's missing race-engine dependency.
- Start backend test subprocesses with the current Node executable rather than a
  nested npx shell process; preserve diagnostic output and child exit failures.
- Correct the stale removed-web-client dev command, align Node to supported 22/24
  LTS majors, and align README license text with the existing Apache-2.0 LICENSE.
  Remove unsupported download/play and platform-verification claims from quick start.

## Concrete remaining blockers

1. **No Unreal host available in this session.** Windows batch invocation, C++ API
   compatibility, actual UAT archive layout and installed-data resolution must be
   verified on UE 5.7. The fake-tool tests establish orchestration behavior only.
2. **No matching Cleveland citypack.** `Cleveland5_0KmWorld.umap` and a level spec
   exist, but `cleveland_5.0km` has no committed semantic citypack. The current map
   cannot stand in for a reproducible historical airport circuit.
3. **Akron input inconsistency.** The manifest references missing
   `akron_buildings.json` while declaring 25,022 buildings. The graph validator
   examines 35,828 roads, while older documentation/backend summary reports 1,370.
   Determine which source snapshot each artifact belongs to before rebuilding.
4. **Akron graph validation failure.** Existing validator reports 52 disconnected
   components, 32 roads in no intersection, 1,015 near-miss endpoint pairs and 63
   out-of-bounds roads. Some disconnection may be legitimate geography or clipping;
   do not snap bridges, tunnels or unrelated roads together to make the metric pass.
5. **Raw OSM snapshot missing.** Reproducible compiler regeneration and five tests
   need the matching snapshot. Fetching today's data would produce a new baseline,
   not reproduce the committed one.
6. **Historical layout not certified.** 2006 is the proposed reference year; a
   dated course plan, georeferenced control points and checked start/finish/barrier
   placement are still required. No course length or exact reconstruction is certified.
7. **Visual/AI gates open.** 145 `.uasset` files and two `.umap` files are present;
   inventory does not establish their object types, materials, physics rigs or polish.
   Two physical racing opponents and the three final lighting environments remain
   to be demonstrated in the package.

## Unreal host execution handoff

Use the reviewed branch on a Windows 11 machine with Unreal 5.7, compatible Visual
Studio C++ tooling/Windows SDK and Python 3.12. From repository root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/build.py --check --engine "C:\Program Files\Epic Games\UE_5.7" --report build-evidence/preflight.json
python scripts/build.py --engine "C:\Program Files\Epic Games\UE_5.7" --config Development --report build-evidence/build.json
```

The second command verifies portable tests; the third verifies tool discovery;
the fourth attempts a real build. No command by itself grants playability status.
Each build creates a timestamped archive under the app's Build/Windows directory;
use its exact path when preparing an installer, not the parent containing multiple runs.
The older installer scripts still require a separate D2 integration/verification pass.

For CI, register labels `self-hosted`, `Windows`, `X64`, `racegps`, `ue5-5.7`, and
set the repository variable `RACEGPS_UE_ROOT` to the engine install root. Dispatch
the reviewed branch/configuration. Download both the evidence and game artifacts.

In Unreal: load both maps and inspect dependencies; compile; verify menu/map/spawn
selection; complete a route in PIE; then install the fresh package on another
machine without the source checkout and repeat. Confirm the packaged resolver reads
the installed citypack and level specs, not a developer directory. Verify that an
unavailable Cleveland pack produces a clear failure rather than an implicit Akron run.

## Cleveland source and scene contract

Reference register: [CLEVELAND_REFERENCE_CONTRACT.md](CLEVELAND_REFERENCE_CONTRACT.md).
Deliverable requirements: one certified airport-course overlay, one production car,
two physical rivals, skyline reference viewpoints, sunset/twilight/midnight scene
presets, and a small internal urban diagnostic fixture. No binary art assets were
fabricated or declared complete during D1.

Next work follows two dependencies: repair/establish an immutable matching city-data
snapshot, and execute the reviewed build on an Unreal host. The full D1/D2 runtime
gate remains blocked until that evidence exists.
