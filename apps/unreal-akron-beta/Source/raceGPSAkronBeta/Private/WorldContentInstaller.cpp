// Copyright raceGPS. All Rights Reserved.

#include "WorldContentInstaller.h"
#include "PreflightSystem.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"

bool UWorldContentInstaller::VerifyInstallation(FString& OutSummary)
{
    TArray<FString> Lines;
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

    const FString GameExe = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / TEXT("Binaries/Win64/raceGPS.exe"));
    const FString ManifestPath = FPaths::ProjectDir() / TEXT("world-content-manifest.json");
    const FString CitypackRoutes = FPaths::ProjectDir() / TEXT("citypacks/akron-oh-beta-001/akron_routes.json");
    const FString InstallerPayload = FPaths::ProjectDir() / TEXT("installer-payload.json");

    auto Record = [&Lines](const FString& Label, bool bOk)
    {
        Lines.Add(FString::Printf(TEXT("%s: %s"), *Label, bOk ? TEXT("OK") : TEXT("MISSING")));
    };

    Record(TEXT("Game executable"), PlatformFile.FileExists(*GameExe));
    Record(TEXT("World content manifest"), PlatformFile.FileExists(*ManifestPath));
    Record(TEXT("Akron citypack routes"), PlatformFile.FileExists(*CitypackRoutes));
    Record(TEXT("Installer payload manifest"), PlatformFile.FileExists(*InstallerPayload));

    const FPreflightCheck WorldCheck = UPreflightSystem::CheckWorldMap();
    Lines.Add(FString::Printf(TEXT("World map: %s"), *WorldCheck.Detail));
    if (!WorldCheck.RecommendedAction.IsEmpty())
    {
        Lines.Add(FString::Printf(TEXT("Recommended: %s"), *WorldCheck.RecommendedAction));
    }

    const TArray<FPreflightCheck> Checks = UPreflightSystem::RunAllChecks();
    const FPreflightSummary Summary = UPreflightSystem::GetSummary(Checks);
    Lines.Add(FString::Printf(
        TEXT("Preflight summary: pass=%d warning=%d fail=%d can_launch=%s"),
        Summary.PassCount,
        Summary.WarningCount,
        Summary.FailCount,
        Summary.bCanLaunch ? TEXT("true") : TEXT("false")));

    for (const FString& Line : Lines)
    {
        UPreflightSystem::AppendPreflightLog(Line);
    }

    OutSummary = FString::Join(Lines, TEXT("\n"));
    return Summary.bCanLaunch;
}

FString UWorldContentInstaller::GetReleasesUrl()
{
    return TEXT("https://github.com/LumenHelixLab/raceGPS/releases");
}

FString UWorldContentInstaller::GetSetupGuideUrl()
{
    return TEXT("https://github.com/LumenHelixLab/raceGPS/blob/main/apps/unreal-akron-beta/README.md#level-setup-guide");
}