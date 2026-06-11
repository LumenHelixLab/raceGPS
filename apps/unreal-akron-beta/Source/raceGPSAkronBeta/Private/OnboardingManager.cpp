// Copyright raceGPS. All Rights Reserved.

#include "OnboardingManager.h"
#include "PreflightSystem.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFilemanager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"

TArray<FString> UOnboardingManager::StepNames = {
    TEXT("Hardware Check"),
    TEXT("Graphics Settings"),
    TEXT("Select City"),
    TEXT("Controls"),
    TEXT("Create Profile")
};

UOnboardingManager* UOnboardingManager::GetInstance()
{
    static UOnboardingManager* Instance = nullptr;
    if (!Instance)
    {
        Instance = NewObject<UOnboardingManager>();
        Instance->AddToRoot();
    }
    return Instance;
}

void UOnboardingManager::StartOnboarding()
{
    CurrentStep = 0;
    OnStepChanged.Broadcast(CurrentStep, StepNames[CurrentStep]);
}

void UOnboardingManager::AdvanceStep()
{
    if (CurrentStep < StepNames.Num() - 1)
    {
        CurrentStep++;
        OnStepChanged.Broadcast(CurrentStep, StepNames[CurrentStep]);
    }
    else
    {
        FinishAndSave();
    }
}

void UOnboardingManager::SkipOnboarding()
{
    CurrentStep = StepNames.Num() - 1;
    FinishAndSave();
}

TArray<FString> UOnboardingManager::GetStepNames() const
{
    return StepNames;
}

void UOnboardingManager::SetSelectedCitypack(const FString& CityId)
{
    SelectedCitypack = CityId;
}

void UOnboardingManager::SetControlScheme(int32 SchemeIndex)
{
    ControlSchemeIndex = FMath::Clamp(SchemeIndex, 0, 2);
}

void UOnboardingManager::SetPlayerName(const FString& Name)
{
    PlayerName = Name.IsEmpty() ? TEXT("Racer") : Name;
}

FString UOnboardingManager::GetStepSubtitle(int32 StepIndex) const
{
    switch (StepIndex)
    {
    case 0: return TEXT("Check your machine before the first night run.");
    case 1: return TEXT("Dial visuals for a smooth, readable street-racing feel.");
    case 2: return TEXT("Pick your city and lock the world you are about to drive.");
    case 3: return TEXT("Set controls that feel natural the moment the countdown ends.");
    case 4: return TEXT("Create a driver identity and save a launch-ready profile.");
    default: return TEXT("Get ready to drive.");
    }
}

FString UOnboardingManager::BuildCompletionMessage(bool bCanLaunch, int32 FailCount, int32 WarningCount) const
{
    if (bCanLaunch)
    {
        return WarningCount > 0
            ? FString::Printf(TEXT("Ready to drive. %d warning(s) noted, but your first run is clear to launch."), WarningCount)
            : TEXT("Ready to drive. Your first run is clear to launch.");
    }

    return FString::Printf(TEXT("Your build needs attention before your first drive. %d blocker(s), %d warning(s)."), FailCount, WarningCount);
}

bool UOnboardingManager::ShouldShowOnboarding()
{
    return UPreflightSystem::IsFirstRun();
}

void UOnboardingManager::FinishAndSave()
{
    const TArray<FPreflightCheck> Checks = UPreflightSystem::RunAllChecks();
    const FPreflightSummary Summary = UPreflightSystem::GetSummary(Checks);
    LastCompletionMessage = BuildCompletionMessage(Summary.bCanLaunch, Summary.FailCount, Summary.WarningCount);
    bLastCanLaunch = Summary.bCanLaunch;
    LastPreflightFailCount = Summary.FailCount;
    LastPreflightWarningCount = Summary.WarningCount;

    // Save onboarding completion
    UPreflightSystem::MarkFirstRunComplete();

    // Write profile settings
    FString ConfigDir = FPaths::ProjectSavedDir() / TEXT("Config");
    FPlatformFileManager::Get().GetPlatformFile().CreateDirectoryTree(*ConfigDir);

    FString ProfilePath = ConfigDir / TEXT("PlayerSettings.json");
    TSharedPtr<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetBoolField(TEXT("onboarding_complete"), true);
    Root->SetStringField(TEXT("version"), TEXT("0.2.0"));
    Root->SetStringField(TEXT("player_name"), PlayerName);
    Root->SetStringField(TEXT("citypack"), SelectedCitypack);
    Root->SetNumberField(TEXT("control_scheme"), ControlSchemeIndex);
    Root->SetStringField(TEXT("graphics_preset"), UPreflightSystem::GetRecommendedGraphicsPreset());
    Root->SetStringField(TEXT("step_0_subtitle"), GetStepSubtitle(0));
    Root->SetStringField(TEXT("step_1_subtitle"), GetStepSubtitle(1));
    Root->SetStringField(TEXT("step_2_subtitle"), GetStepSubtitle(2));
    Root->SetStringField(TEXT("step_3_subtitle"), GetStepSubtitle(3));
    Root->SetStringField(TEXT("step_4_subtitle"), GetStepSubtitle(4));
    Root->SetStringField(TEXT("completion_message"), LastCompletionMessage);
    Root->SetBoolField(TEXT("preflight_can_launch"), Summary.bCanLaunch);
    Root->SetNumberField(TEXT("preflight_fail_count"), Summary.FailCount);
    Root->SetNumberField(TEXT("preflight_warning_count"), Summary.WarningCount);

    FString OutJson;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutJson);
    FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);
    FFileHelper::SaveStringToFile(OutJson, *ProfilePath);

    OnCompleted.Broadcast(Summary.bCanLaunch);
}
