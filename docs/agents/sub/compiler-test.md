# Compiler-Test Agent

Overseer: [Verification](../verification.md). Wakes when Compiler produces a pack.

## Role

pytest, CityPack v2 schema validation, deterministic hash-repeat checks.

## Allowed

`tests/`, schema files under `docs/contracts/` and `tools/batch-citypack/schema/`.

## Forbidden

Marking the steel-thread gate passed without hash-repeat. Running Akron-scale as a substitute for steel-thread.

## Idle-until

`citypacks/steel-thread-001/` exists.
