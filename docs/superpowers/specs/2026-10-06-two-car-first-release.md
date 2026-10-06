# Two-car first release — approved scope

Owner approval: October 6, 2026, conversation. This supersedes three-car requirements for the first release only.

## Product target

One compact Cleveland course, one finished player car and one reliable physical opponent. A polished visual experience takes priority over map size, garage breadth or complex simulation. Perfect one signature lighting treatment before expanding the time-of-day range. Keep launch, race, results and rematch complete.

## Contact contract

Chaos owns the physical response for both vehicles. Do not add a second impact force on top of the solver or give the AI hidden grip, mass or recovery advantages. Real car collision is required; ghost playback does not qualify.

- Sideswipe: brief scrape sound and restrained sparks while surfaces slide.
- Tap: restrained impact sound and the solver's small deflection/speed change.
- Hard impact: stronger collision response and audio, cosmetic damage and optional reduced-motion-aware camera feedback.
- Feedback must reflect relative contact motion/direction and impact impulse, with bounded emission frequency. Absolute world speed is insufficient.
- Cosmetic wear must not silently change performance.
- No automatic penalty for incidental car-to-car contact in this first offline release.
- A reset requires clear space and cannot grant forward progress or a lap. Wait if the destination is occupied.
- AI must brake for a car ahead, allow racing room, react to contact and finish under the same physical rules.

## Current implementation and explicit open gates

The source patch enforces two grid slots, updates HUD field sizes, connects impact sound, exposes per-car Blueprint contact feedback/cosmetic wear and an optional Niagara scrape asset, adds speed/gap-based AI braking, and removes the diagnostic +25m reset jump. Reset paths share clearance checks. Existing Chaos collision remains the only force source.

The C++ policy runs in native portable tests. UE headers, UObject integration, collision response and actual race feel have NOT been compiled/playtested in this environment. Audio/Niagara assets must be assigned and reviewed in Unreal; adding a hook does not establish that sparks or sound are visible/audible. Cosmetic wear is an exposed value, not an authored damage material. Camera shake, scrape audio, passing/side-room logic, shared player/AI progress certification and final tuning remain open.

## Grok/local Unreal handoff — required next work

1. Compile the patch against installed UE 5.7; record exact patch/toolchain, source SHA and logs. Do not merge an uncompiled gameplay change into the release branch.
2. Verify exactly one player and one possessed rival at initial start and after five rematches. A failed pawn/controller spawn must not start a one-car race.
3. Assign licensed collision sound and a short low-flash Niagara scrape effect on the vehicle Blueprint. Bind OnContactFeedback for scrape audio and cosmetic material response. Ensure player preferences govern camera feedback and effects.
4. Run repeatable scenarios at low, medium and high speeds: parallel clean run, equal-speed brush, angled sideswipe, rear tap, hard corner contact, wall strike, stopped rival, rollover and blocked reset. Swap human/AI roles and record relative speed, impulse, feedback type, finish state and recovery location.
5. Confirm no diagnostic forward reset, reset-induced lap credit, repeated sound bursts, duplicate pair effects or AI pushing at full throttle against a stopped car. A clear lane must still permit passing. The current conservative following controller is a foundation, not a completed passing strategy.
6. Tune the existing tire/steering/target-speed presets for recovery and fun. Verify a lap with the restored braking controller before adding further handling layers. Do not restore unconditional full throttle to conceal an underpowered setup.
7. Capture the same contact cases and a complete race in a packaged Win64 build, plus an unedited visual pass of the hero car/course. Then review physics feel, camera, materials, lights, audio and UI together.

Acceptance: both cars can contest a corner and trade paint without losing controllability in mild contact; hard contact is legible and recoverable; no reset improves standings unfairly; results/rematch work; visual/audio feedback is actually present. More opponents and larger courses remain deferred.
