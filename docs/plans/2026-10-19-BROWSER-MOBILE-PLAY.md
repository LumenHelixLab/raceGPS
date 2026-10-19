# raceGPS browser + mobile play path (2026-10-19)

**Status:** started (docs + first Unreal enable). Local only on `grokbot/cleveland-integration`. No push.
**Owner:** Pit Boss. **Chris ask:** playable on phone AND cross-browser (Chrome, Safari, Firefox, Edge) on mobile and desktop before launch.

## Plausibility (honest)

| Target | Reality today |
|--------|----------------|
| Native Android / iOS Unreal app | **Not set up.** No `Platforms/Android` or `IOS`, packaging is `-platform=Win64`, installer is Win64 NSIS. Touch UI is off. Chaos Vehicles + Nanite/Lumen-style night look is a hard mobile port. |
| Unreal → WebGL / WebGPU client | **Not viable for UE 5.7.** Epic dropped the HTML5 target years ago. There is no supported path that cooks this C++ Chaos Vehicles project into a browser WASM/WebGPU build. |
| Desktop PC (current) | **What we ship today.** Win64 Development/Shipping via `package_cleveland_solo.ps1` and `PackagedBuilds\Win64\raceGPSRace.exe`. |
| Console | **Not targeted.** No Switch/PS/Xbox platform folders or packaging. |

**What blocks "just install the game on the phone":** no mobile platform configs, no touch driving input, no mobile rendering/scalability profile, no Android/iOS packaging pipeline, and omni's AMD 880M is a PC host not a phone GPU target.

**What works for Chris's real ask (phone + every major browser):** **Unreal Pixel Streaming** (or a later lighter web remake). The game runs on a Windows host (omni or a small cloud GPU box); the browser only shows the stream and sends input. That is cross-browser on mobile and desktop without rewriting the race stack.

## Chosen path (cheapest with plans Chris already pays for)

1. **Primary (now):** Pixel Streaming 2 / WebRTC from a Win64 packaged `raceGPSRace` (or editor for smoke). Browser client = official Pixel Streaming frontend (works in Chrome, Edge, Firefox; Safari needs WebRTC checks).
2. **Not now:** native Android/iOS store builds (months, licenses, store accounts).
3. **Not now:** full Three.js/Babylon remake (second product). Keep as long-term option if streaming cost or latency is unacceptable.
4. **Docs site only:** `docs/index.html` already notes mobile browsers — that is the marketing site, not the game.

## Performance / UX targets (browser stream)

- Host: 1080p30 minimum, 1080p60 preferred on omni when idle; drop to 720p30 on phone networks.
- Input: keyboard + gamepad first; **on-screen touch steer/throttle** in the Pixel Streaming HTML overlay for phones.
- Latency: aim under ~100 ms RTT on LAN; document WAN limits honestly.
- One concurrent streamer per host until we add a matchmaker.

## Concrete steps

### Done this commit
- [x] Decision + evidence recorded here.
- [x] Enable `PixelStreaming` plugin in `raceGPSAkronBeta.uproject` (engine plugin; no custom plugin folder yet).

### Next (local, still no push)
1. Add `Config/DefaultEngine.ini` Pixel Streaming section (`[PixelStreaming]`, signaller URL placeholder) — editor-safe defaults, disabled until Chris says go on a live streamer.
2. Add `docs/handoff/2026-10-19-BROWSER-PLAY-PIXEL-STREAMING.md` runbook: start signaller, package Win64, open browser URL, phone test matrix (Chrome/Safari/Firefox/Edge).
3. Minimal touch overlay HTML under `apps/unreal-akron-beta/PixelStreaming/www/` (steer + throttle + brake) — wire after streamer smoke on desktop browser.
4. Scalability: mobile-stream preset (lower shadows, no Lumen luxuries over WebRTC) as a named console/exec profile.
5. Chris gate: first live LAN stream smoke on omni Brave + Chris's phone before any cloud host spend.

### Explicitly not started
- Native Android/iOS packaging.
- Purchasing cloud GPU time.
- Changing CruiseSprint GlobalDefaultGameMode or Akron 44312 beta scope.

## Evidence pointers (omni worktree)

- Packaging: `scripts/package_cleveland_solo.ps1` → `-platform=Win64`
- Installer: `installer/racegps-setup.nsi` → `raceGPS-v*-Win64-Setup.exe`
- README: "open-source **desktop** arcade racing game"; Windows release target
- Input: `Config/DefaultInput.ini` → `bAlwaysShowTouchInterface=False`
- No `apps/unreal-akron-beta/Platforms/` tree

## Beta vs launch

Akron 44312 playable beta stays **PC-first**. Browser/mobile stream is a **parallel pre-launch track**, not a Gate 1 substitute.
