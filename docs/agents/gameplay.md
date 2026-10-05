# Gameplay-Loop Overseer

Decoupled from World-Gen on purpose. Proves `CruiseSprintGameMode` on a stock placeholder box level so this lane can run in parallel with world-gen.

## Gate

Menu → spawn → drive → checkpoints → finish → results on a placeholder level. Does **not** require real Akron geometry or Section 2.2.

## Sub-agents

Race-Loop (Week 1 live) · Vehicle/Physics (idle) · UI/UMG (idle until Race-Loop needs a visible PIE path)

## Forbidden

Importing CARLA vehicles without Provenance. Course validation gated on one run’s average speed, collision count, or a mandatory loop. Pretending Section 2.2 passed because the C++ loop exists.
