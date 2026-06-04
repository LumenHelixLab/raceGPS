# WebSocket Protocol

Endpoint:

```text
/ws/rooms/{room_id}
```

Minimum client messages:

- `join_room`
- `leave_room`
- `player_position`
- `chat_message`
- `challenge_signal`
- `game_event`

Example chat:

```json
{
  "type": "chat_message",
  "roomId": "global-cruise",
  "message": "who wants to race downtown?"
}
```

Example signal:

```json
{
  "type": "challenge_signal",
  "roomId": "global-cruise",
  "signal": "flash_lights",
  "challengeType": "quick_sprint"
}
```
