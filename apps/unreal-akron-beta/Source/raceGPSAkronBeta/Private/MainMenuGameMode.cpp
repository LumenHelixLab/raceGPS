// Copyright raceGPS. All Rights Reserved.

#include "MainMenuGameMode.h"
#include "PlayerProfileSaveGame.h"
#include "DayNightCycle.h"

AMainMenuGameMode::AMainMenuGameMode(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMainMenuGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);
    LoadPlayerProfile();
}

void AMainMenuGameMode::StartPlay()
{
    Super::StartPlay();
    SpawnDayNightCycle();
    StartTimeLapse();
}

void AMainMenuGameMode::LoadPlayerProfile()
{
    PlayerProfile = UPlayerProfileSaveGame::LoadProfile();
    if (PlayerProfile)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Menu loaded profile for %s (Level %d)"),
            *PlayerProfile->PlayerName, PlayerProfile->PlayerLevel);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Menu failed to load player profile"));
    }
}

void AMainMenuGameMode::SetMenuState(EMenuState NewState)
{
    if (NewState == CurrentState)
        return;

    EMenuState Previous = CurrentState;
    CurrentState = NewState;
    OnMenuStateChanged.Broadcast(CurrentState, Previous);

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Menu state: %s -> %s"),
        *UEnum::GetValueAsString(Previous), *UEnum::GetValueAsString(CurrentState));
}

void AMainMenuGameMode::StartTimeLapse()
{
    if (MenuDayNightCycle)
    {
        MenuDayNightCycle->TimeScale = TimeLapseScale;
        MenuDayNightCycle->bPaused = false;
    }
}

void AMainMenuGameMode::StopTimeLapse()
{
    if (MenuDayNightCycle)
    {
        MenuDayNightCycle->TimeScale = 1.0f;
    }
}

void AMainMenuGameMode::SpawnDayNightCycle()
{
    if (!DayNightCycleClass)
        return;

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    MenuDayNightCycle = GetWorld()->SpawnActor<ADayNightCycle>(
        DayNightCycleClass, FVector::ZeroVector, FRotator::ZeroRotator, Params);

    if (MenuDayNightCycle)
    {
        MenuDayNightCycle->SetTimeOfDay(12.0f);
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Spawned menu DayNightCycle"));
    }
}
