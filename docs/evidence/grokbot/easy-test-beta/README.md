# Easy Test Beta evidence

This folder is the evidence index and fail-closed grade sheet for the Easy Test Beta milestone. Runtime evidence is recorded only when the operator has the required unlock; this task creates documentation and does not launch, cook, or create an Unreal or Research & Training bot.

## Success-criteria index

| Lane | Done when | Evidence / contract pointers |
|---|---|---|
| Launcher | Wizard + restore; launches Race (mode) + Workshop; clear missing-path CTAs | [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md); launcher screenshots and short notes under `docs/evidence/`; [LAUNCHER_PATH_CONTRACT.md](../../../contracts/LAUNCHER_PATH_CONTRACT.md) |
| Workshop | Auth-less routes through export; Akron compilers wired; honest errors | [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md); export proof and route checklist under `docs/evidence/`; [LAUNCHER_PATH_CONTRACT.md](../../../contracts/LAUNCHER_PATH_CONTRACT.md) |
| Race | HUD + pause/settings playable on Cleveland (Dev OK if no package) | [RACE-HUD-SETTINGS-PLAN.md](RACE-HUD-SETTINGS-PLAN.md); [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md); PIE/`-game` log and rendered screenshots only after Chris unlocks Dev |
| Build contract | Written Package vs Dev layout launcher reads | [LAUNCHER_PATH_CONTRACT.md](../../../contracts/LAUNCHER_PATH_CONTRACT.md); [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md) |
| Research ops | PM research notes exist for chosen stacks; R&T bot briefed/created | [research/](../research/); [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md); R&T bot creation is outside this docs-only task and is fail-closed by O2 |

## Evidence rules

- Use [EVIDENCE-TEMPLATE.md](EVIDENCE-TEMPLATE.md) for each lane note.
- Use [FAIL-CLOSED-CHECKLIST.md](FAIL-CLOSED-CHECKLIST.md) for Unreal PM grading.
- A visual PASS requires a rendered, non-NullRHI screenshot. NullRHI, a black/empty viewport, log-only output, cook output, or an unattended Gate 1 attempt is not visual evidence and is **FAIL-CLOSED**.
- Package mode may be recorded as **awaiting build**; Dev mode remains the team path until Chris unlocks attended runtime evidence.
- Do not change `RACE-HUD-SETTINGS-PLAN.md` as part of evidence capture.
