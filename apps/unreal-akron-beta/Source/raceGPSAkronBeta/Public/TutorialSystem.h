#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "TutorialSystem.generated.h"

USTRUCT(BlueprintType)
struct FTutorialStep
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Id;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Title;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Description;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString InputAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    float AutoAdvanceDelay = 0.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    bool bWaitForInput = true;
};

UCLASS()
class RACEGPSAKRONBETA_API UTutorialSystem : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void StartTutorial();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void AdvanceStep();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void SkipTutorial();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void OnInputReceived(const FString& ActionName);

    UFUNCTION(BlueprintPure, Category = "raceGPS|Tutorial")
    bool IsActive() const { return bActive; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|Tutorial")
    FTutorialStep GetCurrentStep() const;

    UFUNCTION(BlueprintPure, Category = "raceGPS|Tutorial")
    int32 GetCurrentStepIndex() const { return CurrentStepIndex; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|Tutorial")
    int32 GetTotalSteps() const { return Steps.Num(); }

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Tutorial")
    TArray<FTutorialStep> Steps;

protected:
    bool bActive = false;
    int32 CurrentStepIndex = 0;

    UFUNCTION()
    void AutoAdvance();

    FTimerHandle AutoAdvanceTimer;
};
