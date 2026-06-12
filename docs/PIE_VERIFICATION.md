# PIE / Backend Wire Verification

Automated smoke (no UE5 Editor required):

```powershell
cd D:\projects\racegps\apps\backend
npm run dev

# separate terminal
cd D:\projects\racegps
node scripts/verify-ue5-backend-wire.mjs
```

**Pass criteria:** health → session cookie → create room → WebSocket welcome.

## UE5 Editor steps (operator)

1. Start backend (`npm run dev` in `apps/backend`)
2. Open `raceGPSAkronBeta.uproject`
3. Main menu → LAN Browser
4. `bPreferNodeBackend=true` (default) — status should show backend session
5. **Host** → creates room + WebSocket
6. **Refresh** → lists rooms from `GET /api/rooms`

See `docs/UE5_BACKEND_WIRE.md`.