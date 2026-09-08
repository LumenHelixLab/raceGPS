# raceGPS Grokbot Constitution

**Claim level:** OWNER_CONFIRMED (handoff product constitution) + local OBSERVED adaptations
**Gate scope:** G1 only for this execution turn
**Date (local ET):** 2026-09-07

## Product goal
Deliver a recognizable Cleveland airport racing demo with one human driver, two physical AI opponents, convincing arcade handling, and finished Sunset, Twilight and Midnight environments. Real geography, scale, skyline placement and source-informed reconstruction matter.

Provisional historical reference: **2006 Grand Prix of Cleveland at Burke Lakefront Airport**. Do not conflate with 1982 Cleveland 500. Sequence: Cleveland demo -> offline product -> online ZIP championship.

## Chris approvals (G1-G5)
Owner authorized autonomous development through five evidence-based gates, local Unreal use, branch publication / draft-PR preparation. Continue reversible local work without repeated permission prompts.

### Boundaries (must keep)
- No force-push
- No merge to master/default branch
- No purchases / paid cloud infra
- Do not overwrite unrelated user changes or reset dirty checkout
- Do not replace showcase truth feature/cleveland-showcase-demo @ f2a8ecd
- Classify claims: OWNER_CONFIRMED / OBSERVED / REPRODUCED_LOCALLY / PROPOSED / UNVERIFIED / SUPERSEDED
- Keep GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode

### Gate summary
| Gate | Intent | Status authority |
|---|---|---|
| G1 | Local host baseline + D1 bundle reconcile | HOST-BUILD |
| G2 | Coordinate / transform / diagnostic map truth | COORDINATES |
| G3 | Certified bounded Cleveland course + citypack | WORLD-DATA |
| G4 | Packaged solo drive + visual benchmark | HOST-BUILD / VEHICLE / ART |
| G5 | Physical race + independent demo candidate | VEHICLE / ART / VERIFIER |

G2-G5 remain PENDING until their evidence exists. Do not claim them from G1 activity.
