// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "WorldContentInstaller.generated.h"

/**
 * Verifies world-content / installer payload presence for launch readiness.
 * Bounded G1 fix: .cpp existed on D1 baseline without matching public header.
 */
UCLASS(BlueprintType)
class RACEGPSAKRONBETA_API UWorldContentInstaller : public UObject
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "WorldContent")
	static bool VerifyInstallation(FString& OutSummary);

	UFUNCTION(BlueprintPure, Category = "WorldContent")
	static FString GetReleasesUrl();

	UFUNCTION(BlueprintPure, Category = "WorldContent")
	static FString GetSetupGuideUrl();
};
