# raceGPS browser + mobile play path (2026-10-19)

**Status: PAUSED — resumes after launch** (updated 2026-10-19 ~12:06 ET)
**Not canceled.** Chris deferred mobile/cross-browser. Version 2 will carry mobile. No promised deliverables or dates.
**Do not resume** Pixel Streaming setup, WebGL evaluation, or mobile packaging until after raceGPS has launched and is showing action, then Chris (or standing direction) restarts this track.

**Desktop Win64 race beta: untouched.** Continue Akron 44312 / `grokbot/cleveland-integration` PC work as before.

## Standing product direction (Chris, 2026-10-19)

1. **Very fun** — fun is a hard requirement for beta and v2, not a nice-to-have.
2. **Free to play** — no paid gate to play the game.
3. **Name-protected** — modified forks must not be allowed to keep calling themselves RaceGPS (trademark / license / brand work; no public filings without Chris OK).

## Why paused (evidence still true)

| Target | Reality |
|--------|---------|
| Native Android / iOS | Not set up. Packaging is Win64. |
| UE → WebGL / WebGPU | Not viable for UE 5.7 Chaos Vehicles stack. |
| Cross-browser play | Realistic path was Pixel Streaming (host PC → browser). **Parked for v2.** |
| Desktop Win64 | Current ship target. |

## What was started then stopped (local only)

- Commit `37e8589`: this plan + briefly enabled `PixelStreaming` in `raceGPSAkronBeta.uproject`.
- Follow-up pause commit: plugin disabled again; status set to paused. **Nothing pushed.** No signaller, no streamer smoke, no touch overlay, no cloud GPU.

## When this track reopens (after launch)

1. Re-enable Pixel Streaming (or re-evaluate if Epic/stack changed).
2. Signaller + LAN smoke (desktop browser, then phone browsers).
3. Touch overlay for mobile browsers.
4. Only then consider native store builds if still needed.

## Explicitly forbidden until reopen

- Pixel Streaming / WebRTC setup work
- WebGL evaluation as an active task
- Android / iOS packaging
- Spending on cloud stream hosts for this track
