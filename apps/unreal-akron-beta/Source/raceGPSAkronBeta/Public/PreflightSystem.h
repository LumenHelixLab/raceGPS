// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PreflightSystem.generated.h"

UENUM(BlueprintType)
enum class EPreflightStatus : uint8
{
    Pass        UMETA(DisplayName = "Pass"),
    Warning     UMETA(DisplayName = "Warning"),
    Fail        UMETA(DisplayName = "Fail"),
    Unknown     UMETA(DisplayName = "Unknown"),
};

USTRUCT(BlueprintType)
struct FPreflightCheck
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    FString Category;

    UPROPERTY(BlueprintReadOnly)
    FString Description;

    UPROPERTY(BlueprintReadOnly)
    EPreflightStatus Status = EPreflightStatus::Unknown;

    UPROPERTY(BlueprintReadOnly)
    FString Detail;

    UPROPERTY(BlueprintReadOnly)
    FString RecommendedAction;
};

USTRUCT(BlueprintType)
struct FPreflightSummary
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    int32 TotalChecks = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 PassCount = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 WarningCount = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 FailCount = 0;

    UPROPERTY(BlueprintReadOnly)
    bool bCanLaunch = false;

    UPROPERTY(BlueprintReadOnly)
    FString RecommendedGraphicsPreset;
};

/**
 * Runtime preflight system: validates hardware, OS, drivers, and game data
 * before allowing the player into the main menu.
 */
UCLASS(Blueprintable, BlueprintType)
class RACEGPSAKRONBETA_API UPreflightSystem : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Preflight")
    static TArray<FPreflightCheck> RunAllChecks();

    UFUNCTION(BlueprintCallable, Category = "Preflight")
    static FPreflightSummary GetSummary(const TArray<FPreflightCheck>& Checks);

    UFUNCTION(BlueprintPure, Category = "Preflight")
    static FString GetRecommendedGraphicsPreset();

    UFUNCTION(BlueprintCallable, Category = "Preflight")
    static bool IsFirstRun();

    UFUNCTION(BlueprintCallable, Category = "Preflight")
    static void MarkFirstRunComplete();

    UFUNCTION(BlueprintCallable, Category = "Preflight")
    static FString GetSaveDirectoryStatus();

private:
    static FPreflightCheck CheckOS();
    static FPreflightCheck CheckRAM();
    static FPreflightCheck CheckDiskSpace();
    static FPreflightCheck CheckGPU();
    static FPreflightCheck CheckCitypackIntegrity();
    static FPreflightCheck CheckSaveDirectory();
    static FPreflightCheck CheckNetwork();
};
