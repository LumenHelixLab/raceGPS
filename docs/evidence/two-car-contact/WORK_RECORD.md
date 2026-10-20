# Two-car contact work record

Base: grokbot/cleveland-integration at 9604d0bcf99c8019e84852bbc8a11990608af39c.
Scope authority: user approval on October 6, 2026. Isolated clone/feature branch; no changes to the user's Windows checkout.

Ruling: apply the newly approved two-car scope rather than execute the older three-car convergence plan. Cost: broader integration and release work remain separate.
Ruling: preserve Chaos collision impulses; add presentation and AI gap control instead of synthetic shoves. Cost: feel must be tuned on an actual Unreal host.
Ruling: remove the diagnostic forward reset as well as runtime forward-reset behavior so automated evidence cannot pass by jumping around the course.

Baseline Python: 263 passed, 5 skipped. Five legacy source cases skipped because akron_raw.osm is absent.
Native policy test: RED (missing production policy), then compiled and exercised actual production header; a distant-following case caught excessive slowing, corrected before GREEN.
Initial full suite after patch: 264 passed, 5 skipped. UE integration remains uncompiled on this host.

No baseline Node issue is claimed fixed by this C++ patch. No new art/audio assets were fabricated. Release readiness remains open; see the two-car scope spec for exact local gates.

Fresh independent source review found: duplicate feedback ownership for locally controlled AI; recovery bypassing following controls; startup callers ignoring grid failure; presentation assets absent.
Fixed ownership with a native-tested pair selector (RED compile failure before implementation, then GREEN). Moved proximity constraints into final ApplyCommands so recovery also obeys them; recovery now settles and gently rejoins. Added startup guards and possession checks.
Ruling: absent authored scrape/damage/camera assets remain explicit Unreal handoff gates; do not synthesize low-quality placeholders or claim a finished visual effect. Cost: this draft remains blocked for release until assets and packaged play are reviewed.
Final portable run: 264 passed, 5 skipped in 6.50 seconds. No Unreal engine compilation or playtest executed. Source review is not a substitute.
