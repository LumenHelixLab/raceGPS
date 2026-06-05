#include "TutorialSystem.h"

void UTutorialSystem::StartTutorial()
{
    if (Steps.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] No tutorial steps defined"));
        return;
    }

    bActive = true;
    CurrentStepIndex = 0;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Tutorial started. Steps: %d"), Steps.Num());

    if (Steps[0].AutoAdvanceDelay > 0.0f)
    {
        GetWorld()->GetTimerManager().SetTimer(AutoAdvanceTimer, this, &UTutorialSystem::AutoAdvance, Steps[0].AutoAdvanceDelay, false);
    }
}

void UTutorialSystem::AdvanceStep()
{
    if (!bActive)
        return;

    CurrentStepIndex++;
    if (CurrentStepIndex >= Steps.Num())
    {
        SkipTutorial();
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Tutorial step %d: %s"), CurrentStepIndex, *Steps[CurrentStepIndex].Title);

    GetWorld()->GetTimerManager().ClearTimer(AutoAdvanceTimer);
    if (Steps[CurrentStepIndex].AutoAdvanceDelay > 0.0f)
    {
        GetWorld()->GetTimerManager().SetTimer(AutoAdvanceTimer, this, &UTutorialSystem::AutoAdvance, Steps[CurrentStepIndex].AutoAdvanceDelay, false);
    }
}

void UTutorialSystem::SkipTutorial()
{
    bActive = false;
    CurrentStepIndex = 0;
    GetWorld()->GetTimerManager().ClearTimer(AutoAdvanceTimer);
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Tutorial ended"));
}

void UTutorialSystem::OnInputReceived(const FString& ActionName)
{
    if (!bActive || CurrentStepIndex >= Steps.Num())
        return;

    const FTutorialStep& Step = Steps[CurrentStepIndex];
    if (Step.bWaitForInput && Step.InputAction == ActionName)
    {
        AdvanceStep();
    }
}

FTutorialStep UTutorialSystem::GetCurrentStep() const
{
    if (CurrentStepIndex >= 0 && CurrentStepIndex < Steps.Num())
        return Steps[CurrentStepIndex];
    return FTutorialStep();
}

void UTutorialSystem::AutoAdvance()
{
    AdvanceStep();
}
