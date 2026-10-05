raceGPS — Local Unreal build kit (no Grok required)
Lumen Helix Solutions — LumenHelix.com

CHECKPOINT: b379681a1e236d2b06cc97d8d9b13457d8fd4293
This is a SOURCE BUILD KIT, not a game installer. PowerShell launcher prepared
but not executed on Windows by this session. Unreal/UHT compilation remains pending.

1. Extract the whole ZIP into a writable folder. Open PowerShell in that folder.
2. With Unreal still open, run:

   .\Build-RaceGPS-Local.ps1 -CheckOnly

3. If discovery succeeds, SAVE YOUR WORK and CLOSE Unreal Editor, then run:

   .\Build-RaceGPS-Local.ps1

4. Attach the resulting raceGPS-evidence-<timestamp>.zip in this ChatGPT conversation.
   That lets this assistant diagnose the actual local compiler results.

The script assumes your existing checkout is D:\projects\raceGPS.
To override repository or engine location, use the real verified paths, for example:

   .\Build-RaceGPS-Local.ps1 -Repo 'E:\Projects\raceGPS' -Engine 'D:\Epic Games\UE_5.7' -CheckOnly

Repeat those overrides for the real build. Unreal 5.7.4 is compatible with the
project's declared 5.7 requirement. The script reads the actual Build.version.
It detects an active editor and stops; it does not kill it or attempt Live Coding.

Required: existing raceGPS Git checkout, Git, Python 3.12 available through the
Windows py launcher, Unreal 5.7, and the Unreal Windows C++ toolchain/SDK.
If script execution is blocked by machine policy, retain the exact error and report
it; this kit does not change security policy. No administrator operation is included.

The bundle is incremental and requires repository base commit:
b56b6c814c23423d13b7683607d0da5ba89130f2
If your checkout lacks that commit, preserve your work and fetch legitimate history
from the existing origin. If access or the repository is absent, report the exact
error rather than substituting an unrelated folder or resetting existing work.

The script verifies bundle hash/prerequisites, imports the checkpoint into a new
worktree/branch beside the original checkout, uses an isolated Python environment,
runs portable tests, retains the expected legacy Akron audit failure, and attempts
raceGPSAkronBetaEditor Win64 Development. It does not overwrite the original working
checkout, alter old map assets, push to GitHub, package a release or claim a playable game.
Any newer local work remains preserved in the original checkout for later integration.

Current limits: real Cleveland historical circuit/grid not certified; old Akron data
is inconsistent; migrated scenes/assets still need engine verification. A successful
editor build is the next evidence gate, not the final game.
