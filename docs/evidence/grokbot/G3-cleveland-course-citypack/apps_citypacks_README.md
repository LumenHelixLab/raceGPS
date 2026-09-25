# Cleveland citypacks (apps tree)

This directory is **gitignored** (see root `.gitignore`).

On a Windows host, create the local junction to the canonical pack:

```powershell
powershell -File scripts/link_cleveland_citypack.ps1
```

That links `burke_gp_1997` → `../../../../citypacks/cleveland/burke_gp_1997`.

Do not maintain a second copy of pack files here.