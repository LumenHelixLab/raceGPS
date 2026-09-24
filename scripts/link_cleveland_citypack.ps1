# Creates apps/unreal-akron-beta/citypacks/cleveland/burke_gp_1997 as a junction
# to the canonical repo-root citypacks/cleveland/burke_gp_1997 (single source of truth).
$ErrorActionPreference = "Stop"
$Repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$Canonical = Join-Path $Repo "citypacks\cleveland\burke_gp_1997"
$Parent = Join-Path $Repo "apps\unreal-akron-beta\citypacks\cleveland"
$Link = Join-Path $Parent "burke_gp_1997"
if (-not (Test-Path $Canonical)) { throw "Canonical pack missing: $Canonical" }
New-Item -ItemType Directory -Force -Path $Parent | Out-Null
if (Test-Path $Link) {
  $item = Get-Item $Link -Force
  if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    cmd /c "rmdir `"$Link`""
  } else {
    throw "Refusing to remove non-junction path: $Link"
  }
}
cmd /c "mklink /J `"$Link`" `"$Canonical`""
Write-Host "OK: $Link -> $Canonical"