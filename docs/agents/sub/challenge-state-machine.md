# Challenge State-Machine Agent

Overseer: [Control-Plane](../control-plane.md). Week 1: **idle**. TypeScript, not Java.

## Role

Offered → Reserved → Lobby → Countdown → Racing → ResultPending → Settled. Idempotency keys. Compare-and-swap transitions. Must match the Java-Backend `ChallengeService` design, not diverge.

## Forbidden

A different machine than Java. RabbitMQ. Standing up multiplayer-alpha before the merge-on-real-map trigger.

## Idle-until

Control-Plane overseer is unblocked.
