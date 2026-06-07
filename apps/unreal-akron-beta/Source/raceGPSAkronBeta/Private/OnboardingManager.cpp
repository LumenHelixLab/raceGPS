// Copyright raceGPS. All Rights Reserved.

#include "OnboardingManager.h"
#include "PreflightSystem.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformFilemanager.h"

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

bool UOnboardingManager::ShouldShowOnboarding()
{
    return UPreflightSystem::IsFirstRun();
}

void UOnboardingManager::FinishAndSave()
{
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

    FString OutJson;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutJson);
    FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);
    FFileHelper::SaveStringToFile(OutJson, *ProfilePath);

    OnCompleted.Broadcast(true);
}
