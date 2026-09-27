# BE read-along — Pack 01 annotations (Win64 Dev rebuild + log forensics)

**Annotator:** Build & Engine  
**Date:** 2026-09-26  
**Parent pack (primary):** [2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md](./2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md)  
**Sibling stub:** [2026-09-26-PACK-01-REBUILD-AND-LOG-FORENSICS.md](./2026-09-26-PACK-01-REBUILD-AND-LOG-FORENSICS.md) (Prototyper seed — read-along only; superseded for depth by WIN64-DEV parent)  
**Mode:** study notes only — no editor, no PIE, no `LaunchClevelandRace`, no UBA experiment, no Gate 1 spam

### Parent cites (in-tree / handoff)

| Cite | Why it matters |
|------|----------------|
| `docs/evidence/grokbot/G6-race-base-mvp/track-b-phase-a-build.log` | Concrete Succeeded rebuild: `-WaitMutex -MaxParallelActions=1 -NoUBA -NoXGE`; `Result: Succeeded` (~10.5s) |
| `2026-09-25-GATE1-TRACK-B-PHASE-A-LANDED.md` | Phase A TEMP probe landed; prior UBA OOM; CruiseSprint untouched |
| `2026-09-25-GATE1-TRACK-B-DIG.md` | ViewportClosed ~1.85s after Racing; playtest-only RequestExit sites ruled out when `playtest=0` |
| `2026-09-25-GATE1-BOTH-TRACKS.md` / `GATE1-RESUME-PLAYBOOK.md` | Track A human keep-alive; no unattended agent launches |
| `2026-09-25-GATE1-TRACK-B-PATCH-PLAN.md` | Phase B viewport subclass still **HOLD** |
| `apps/unreal-akron-beta/LaunchClevelandRace.bat` | Human default vs `playtest` vs `nullrhi` contracts |
| `G1-host-baseline/VERDICT.md` + `HOST_INVENTORY.md` | Live Coding → Build exit **6**; omni iGPU / ~31 GB RAM |
| `2026-09-25-TECH-SPEC-SHEET.md` / `UNLOCK-CRITERIA.md` | Build.bat shape; modes A–D; never-PASS list |
| RS sibling | `../race-systems-training/` — session / finish+R semantics (BE owns process survival) |

---

## What this pack is for (BE lane)

Own **how omni builds and how logs prove exits**. When freeze lifts, Build & Engine keeps a single editor owner, a known-good Win64 Development recipe, and a grep cheat sheet that separates ViewportClosed / RequestExit / Track B probes from false PASS noise.

Race Systems owns race-loop semantics (countdown → finish HUD → R). Build & Engine owns whether the process stayed alive long enough for those semantics to matter. Workshop Web owns `.rgpack` / Workshop routes — BE may package Workshop targets later, but does not redesign the two-app split. World Environment owns visual stills under Mode B — BE owns bats / one-editor slot when capture reopens.

---

## Steal (map to raceGPS)

1. **Phase A NoUBA recipe as default on omni** — Logged UBT line uses `-MaxParallelActions=1 -NoUBA -NoXGE` and ended `Result: Succeeded`. Prefer that until a measured UBA pass with RAM headroom exists. Do not re-enable UBA as "faster" without evidence.
2. **One UnrealEditor / one `-game` on omni** — iGPU Radeon 880M; Live Coding with editor open → Build exit **6**. Kill other editors/games before rebuild or Gate 1. Never stack agent editor against Chris's attended Showcase window.
3. **Human-default bat contract** — `LaunchClevelandRace.bat Sunset` → preset + `-log -windowed -ResX=1600 -ResY=900` only. No `-ClevelandAutoLap`, no `-nullrhi` for Gate 1. Showcase GM via URL override; CruiseSprint GlobalDefault stays.
4. **Track A is the discriminating ViewportClosed test** — Explorer double-click, keep focus ≥60–120s after Racing (ideally finish+R). If attended survives → root cause is session/ownership, not race logic. Agent unattended `-game` is not Gate 1 evidence.
5. **Grep sheet before guessing** — `raceGPS TrackB:`, `ViewportClosed`, `RequestExit`, `UGameEngine::Tick.ViewportClosed`, `EndRace`, `RestartShowcase`, `playtest=`. GameMode RequestExit ~L415/~L620 is playtest-only.
6. **Phase A landed / Phase B HOLD** — TEMP 1 Hz heartbeat + VIEWPORT LOST Warning already in Showcase `Tick`. Do not freestyle a viewport subclass until Prototyper/Chris green Phase B.
7. **Evidence naming habit** — Keep SUCCEEDED rebuild logs (flags + Result) beside FAIL notes; never overwrite FAIL. Attended drops: `track-b-attended-*.log`, `finish-r-PASS-*.txt` under `G6-race-base-mvp/`.
8. **Path hygiene** — Canonical worktree `C:\projects\raceGPS-grokbot-cleveland`. Grep bats for `PROJ=` vs legacy `C:\projects\racegps` before claiming a rebuild.

---

## Do not steal

- Unattended `LaunchClevelandRace` / `Start-Process -game` framed as Gate 1 PASS.
- NullRHI / `ClevelandProofFinishR` / black void as Gate 1 evidence.
- Flipping `GlobalDefaultGameMode` off CruiseSprint.
- UBA-on rebuilds after known OOM without a mitigation note and a Succeeded companion log.
- Multiple concurrent UnrealEditor instances fighting omni GPU/session.
- Owning Showcase finish+R semantics (Race Systems) or `.rgpack` route design (Workshop Web) from this lane.
- Selling empty Workshop/Race packaging targets as progress before race base / unlock.
- Claiming packaging PASS without logged exits + reproduce steps.

---

## Scratch / FAIL notes (docs only — not PASS)

| Artifact | Read |
|----------|------|
| `finish-r-windowed-viewportclosed.log` / excerpts | Racing → ViewportClosed ~1.85s; Gate 1 FAIL shape |
| `finish-r-attempt3-nullrhi-no-progress.log` / proof notes | NullRHI path — **explicitly not Gate 1 PASS** |
| `finish-r-focuskeeper.txt` | HWND keep died ~16ms — supports ownership hypothesis |
| `track-b-phase-a-build.log` | **Succeeded** rebuild cite for NoUBA / MaxParallelActions=1 |
| `ue-editor-build.log` (G6) | Separate Succeeded UBA-local incremental — do not confuse with the Phase A NoUBA recipe as the omni default |

---

## FUTURE observables (do not run now)

When Chris unlocks Mode C (interactive Gate 1) and single-editor omni is free:

| Check | Pass looks like |
|-------|-----------------|
| Rebuild | `raceGPSAkronBetaEditor` Win64 Development with `-MaxParallelActions=1 -NoUBA` → `Result: Succeeded`; log retained under G6 or G1-style meta |
| One-editor | Only one UnrealEditor/`-game` on omni during the run |
| Launch | Human `LaunchClevelandRace.bat Sunset` (no nullrhi / no AutoLap default) |
| Survive | Window focused ≥60–120s after Racing; ideally EndRace + RestartShowcase with **no** ViewportClosed |
| Grep | Log shows TrackB heartbeats (while TEMP remains) or clean EndRace/R path without engine ViewportClosed exit |
| Evidence | `finish-r-PASS-*.txt` + finish HUD shot + after-R shot + log excerpt under `docs/evidence/grokbot/G6-race-base-mvp/` |
| Anti | No NullRHI / void / unattended agent spawn sold as PASS |

Mode D (full agent game) needs a separate Chris unlock beyond C. Packaging Workshop targets pairs with Workshop Web after race base.

---

## Tie-back to known raceGPS debt (docs only)

- Soft gaps cleared 2026-09-26: single Pack 01 filename (WIN64-DEV primary); G6 `track-b-phase-a-build.log` cite.
- Gate 1 FAIL-closed (`b5e1b4b`): windowed Sunset reached Racing then ViewportClosed. Annotations do not fix viewport survival — they document the rebuild + forensics contract for when Mode C reopens.
- Track B Phase A probe is live in Showcase GM only; Phase B HOLD; strip TEMP logs after dig closes (Race Systems).
- G1 Live Coding exit **6** remains a standing omni trap — close editor before Build.bat.

---

## Hand-off

Unreal PM cross-cuts Wave 1 into `agent-training/2026-09-26-WAVE1-TRAINING-QA.md`. This annotations file is BE Pack 01 study depth. Race Systems owns finish+R behavior on a living viewport. Workshop Web owns rgpack export truth. World Environment / Course Architect own Mode B stills — BE frees or holds the single editor slot.