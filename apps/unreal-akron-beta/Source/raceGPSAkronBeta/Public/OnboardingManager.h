// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PreflightSystem.h"
#include "OnboardingManager.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnOnboardingStepChanged, int32, StepIndex, const FString&, StepName);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnOnboardingCompleted, bool, bSuccess);

/**
 * Orchestrates the first-run onboarding experience:
 * 1. Hardware preflight
 * 2. Graphics auto-config
 * 3. Citypack selection / download
 * 4. Control scheme selection
 * 5. Save profile creation
 */
UCLASS(Blueprintable, BlueprintType)
class RACEGPSAKRONBETA_API UOnboardingManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintAssignable, Category = "Onboarding")
    FOnOnboardingStepChanged OnStepChanged;

    UPROPERTY(BlueprintAssignable, Category = "Onboarding")
    FOnOnboardingCompleted OnCompleted;

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    static UOnboardingManager* GetInstance();

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void StartOnboarding();

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void AdvanceStep();

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void SkipOnboarding();

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    int32 GetCurrentStep() const { return CurrentStep; }

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    TArray<FString> GetStepNames() const;

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void SetSelectedCitypack(const FString& CityId);

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void SetControlScheme(int32 SchemeIndex);

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void SetPlayerName(const FString& Name);

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    static bool ShouldShowOnboarding();

    UFUNCTION(BlueprintCallable, Category = "Onboarding")
    void FinishAndSave();

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    FString GetStepSubtitle(int32 StepIndex) const;

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    FString BuildCompletionMessage(bool bCanLaunch, int32 FailCount, int32 WarningCount) const;

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    FString GetLastCompletionMessage() const { return LastCompletionMessage; }

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    bool CanLaunchFromLastPreflight() const { return bLastCanLaunch; }

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    int32 GetLastPreflightFailCount() const { return LastPreflightFailCount; }

    UFUNCTION(BlueprintPure, Category = "Onboarding")
    int32 GetLastPreflightWarningCount() const { return LastPreflightWarningCount; }

protected:
    static TArray<FString> StepNames;
    int32 CurrentStep = -1;

    FString SelectedCitypack = TEXT("akron-oh-beta-001");
    int32 ControlSchemeIndex = 0;
    FString PlayerName = TEXT("Racer");
    FString LastCompletionMessage;
    bool bLastCanLaunch = false;
    int32 LastPreflightFailCount = 0;
    int32 LastPreflightWarningCount = 0;
};
