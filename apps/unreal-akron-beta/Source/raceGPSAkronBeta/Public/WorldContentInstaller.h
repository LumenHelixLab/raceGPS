// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "WorldContentInstaller.generated.h"

UCLASS(Blueprintable, BlueprintType)
class RACEGPSAKRONBETA_API UWorldContentInstaller : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    static bool VerifyInstallation(FString& OutSummary);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    static FString GetReleasesUrl();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    static FString GetSetupGuideUrl();
};