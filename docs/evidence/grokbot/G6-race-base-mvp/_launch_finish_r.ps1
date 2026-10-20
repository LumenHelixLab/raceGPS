$UE = "C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe"
$PROJ = "C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject"
$MAPGAME = "/Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode"
$arg = "`"$PROJ`" `"$MAPGAME`" -game -ClevelandPreset=Sunset -ClevelandSkipIntro -ClevelandAutoDrive -log -windowed -ResX=1600 -ResY=900"
$p = Start-Process -FilePath $UE -ArgumentList $arg -PassThru
$p.Id | Out-File "C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\G6-race-base-mvp\finish-r-pid.txt" -Encoding ascii
"launched PID=$($p.Id) at $(Get-Date -Format o)" | Out-File "C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\G6-race-base-mvp\finish-r-launch.txt" -Encoding utf8
