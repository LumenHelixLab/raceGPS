# Gate 1 BOTH tracks - locked 2026-09-25 (Chris answered t53s622: both)

**Decision:** Unblock Gate 1 with **both**
1. **Track A — Interactive keep-alive** (Chris / attended omni session owns the window)
2. **Track B — ViewportClosed dig** (why `UGameEngine::Tick.ViewportClosed` ~2s after Racing)

NullRHI / ForceFinish still **not** Gate 1 PASS.

---

## Track A — Chris keep-alive (do this for Gate 1 evidence)

### Preconditions
- One Unreal only on omni (kill other editors/games first)
- Sit at the machine or an attended interactive session (not a headless agent spawn)
- Freeze on other lanes can stay; this is Gate 1 only

### Steps
1. Open Explorer to `C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\`
2. Double-click / run human default:
   `LaunchClevelandRace.bat Sunset`
   (human default = preset + `-log -windowed` only — **no** `playtest`, **no** `nullrhi`, **no** `ClevelandAutoLap`)
3. When the window appears: click it once, leave it focused. Do not Alt+Tab away for the first 2–3 minutes.
4. Let Countdown → Racing happen. Drive a lap (or watch AutoDrive if enabled on that build — if cars sit still, note thr=0; that is Vehicle Arcade, still try to keep window alive).
5. On finish HUD, press **R**. Confirm restart without the process quitting.
6. Drop under `docs\evidence\grokbot\G6-race-base-mvp\`:
   - screenshot finish HUD
   - screenshot after R
   - log excerpt with EndRace + RestartShowcase and **no** ViewportClosed
   - note named `finish-r-PASS-*.txt`

### If it dies ~2s after Racing again
- Still a Track B bug. Save the new log next to FAIL notes (do not overwrite).
- Try once more **fullscreen** (remove `-windowed` or use fullscreen toggle) with the same focus rule.
- Do **not** fall back to nullrhi for PASS.

### Agent rule
Agents must **not** spam LaunchClevelandRace from unattended sessions for Gate 1. Track A is human-owned.

---

## Track B — ViewportClosed dig (agent / Race Systems)

### Proven from FAIL logs
- Flags on failing assisted run: `playtest=0 autodive=1 skipIntro=1 proofFinishR=0`
- Timeline: Countdown → Racing → **~1.8s** → `RequestExit(…, UGameEngine::Tick.ViewportClosed)`
- GameMode `RequestExit` sites are playtest-only (stuck speed0 / EndRace playtest). They did **not** fire (playtest=0; no playtest quit log).
- Focus-keeper script reported **DEAD within ~16ms** — external focus keep did not hold the HWND.

### Suspects (ordered)
1. **-game window without durable interactive owner** (agent Start-Process / remote session) — viewport destroyed when session/focus drops.
2. **GameViewport becomes null** → engine Tick ViewportClosed path (engine, not our RequestExit).
3. Focus-keeper ineffective / racing the exit.
4. Less likely: intentional game quit (ruled out for playtest=0 path).

### Dig tasks (no nullrhi PASS; prefer read+patch plan before mass launches)
1. Add temporary logs when GameViewport is lost / window deactivated (Race Systems).
2. Reproduce **only** under attended Track A (Chris keeps window) to see if ViewportClosed disappears — if yes, root cause is session/ownership, not race logic.
3. If attended still dies: search slate/window close, `-FixedSeed`/DPI, multi-monitor, and whether `start "…" UnrealEditor … -game` returns a console that closes the child (bat uses `start` — verify HWND lifetime).
4. Do **not** treat `ClevelandProofFinishR` nullrhi as Gate 1.

### Code map (grokbot-cleveland tree)
- `ClevelandShowcaseGameMode.cpp` — playtest RequestExit ~415 / ~620; ProofFinishR ForceFinish ~463+; RestartShowcase no exit ~646
- `LaunchClevelandRace.bat` — human default: preset + windowed; `playtest` adds AutoLap; `nullrhi` mode rejected for Gate 1

---

## Sync with unlock sheet
- Track A = unlock mode **C** (interactive Gate 1)
- Track B = engineering under mode C (attended repro) — not a license to spam unattended -game
- Modes B (Burke stills) and D (full agent game) still need separate Chris unlock

Updated: 2026-09-25 ~07:55 ET Prototyper
