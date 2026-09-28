# Unreal PM FAIL-CLOSED checklist

Use this grade sheet for Easy Test Beta evidence. A gate is PASS only when its stated proof exists. Otherwise record FAIL or BLOCKED with the missing artifact and next unblock.

| Gate | Question | PASS only if | Result / evidence |
|---|---|---|---|
| L1 | Wizard restores settings? | File round-trip + screenshot |  |
| L2 | Play Race respects mode? | Package -> awaiting-build CTA **or** exe spawn; Dev -> bat start; no NullRHI from UI |  |
| L3 | Open Workshop routes? | Auth-less walk to export |  |
| W1 | Fixture export PASS? | `python -m rgpack` RESULT PASS + UI log |  |
| W2 | Validate fail surfaces log? | Deliberate bad path shows stderr |  |
| R1 | HUD/settings notes cite Akron patterns? | Doc links resolve |  |
| R2 | Runtime Race evidence? | Only after Chris unlock; screenshots are rendered and not NullRHI |  |
| B1 | Path contract written? | `docs/contracts/LAUNCHER_PATH_CONTRACT.md` |  |
| O1 | Research folder exists? | Task 0 files present |  |
| O2 | R&T bot created by this plan? | **Must be NO. PASS only if the R&T bot was NOT created by this plan.** |  |

## Global fail-closed rules

- Any claimed **visual PASS** made with NullRHI is **FAIL-CLOSED** and must be marked FAIL, even when logs report success.
- A black or empty viewport, log-only run, cook output, or unattended Gate 1 attempt is not visual evidence.
- Runtime Race evidence is blocked until Chris unlocks attended Dev testing; Package mode may remain **awaiting build**.
- The human launcher Play Race path must not add `nullrhi`, `-unattended`, `playtest`, or `-ClevelandAutoLap`.
- Do not create a Research & Training bot as part of this plan. O2 is PASS only when it was **not** created.

## Grade record

**Reviewer / Unreal PM:**
**Review timestamp:** <YYYY-MM-DD HH:mm America/New_York>
**Overall result:** PASS | FAIL | BLOCKED
**Blocking gates / next action:**
