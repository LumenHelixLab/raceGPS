// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MainMenuGameMode.generated.h"

UENUM(BlueprintType)
enum class EMenuState : uint8
{
    Title       UMETA(DisplayName = "Title"),
    Main        UMETA(DisplayName = "Main"),
    Garage      UMETA(DisplayName = "Garage"),
    Settings    UMETA(DisplayName = "Settings"),
    Credits     UMETA(DisplayName = "Credits")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnMenuStateChanged, EMenuState, NewState, EMenuState, PreviousState);

/**
 * GameMode for the main menu level.
 * Loads player profile, drives an animated DayNightCycle background,
 * and manages the menu state machine (Title -> Main -> Garage -> Settings -> Credits).
 */
UCLASS()
class RACEGPSAKRONBETA_API AMainMenuGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMainMenuGameMode(const FObjectInitializer& ObjectInitializer);

    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
    virtual void StartPlay() override;

    /** Transition to a new menu state. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void SetMenuState(EMenuState NewState);

    /** Get current menu state. */
    UFUNCTION(BlueprintPure, Category = "raceGPS|Menu")
    EMenuState GetMenuState() const { return CurrentState; }

    /** Load or create the player profile. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void LoadPlayerProfile();

    /** Start the DayNightCycle time-lapse effect. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void StartTimeLapse();

    /** Stop the time-lapse and return to normal speed. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void StopTimeLapse();

    /** Delegate fired whenever the menu state changes. */
    UPROPERTY(BlueprintAssignable, Category = "raceGPS|Menu")
    FOnMenuStateChanged OnMenuStateChanged;

    /** DayNightCycle class to spawn for the menu background. */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    TSubclassOf<class ADayNightCycle> DayNightCycleClass;

    /** Time scale multiplier for the menu background time-lapse. */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    float TimeLapseScale = 60.0f;

    /** Currently loaded player profile. */
    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Menu")
    TObjectPtr<class UPlayerProfileSaveGame> PlayerProfile;

    /** Spawned DayNightCycle actor for the menu scene. */
    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Menu")
    TObjectPtr<class ADayNightCycle> MenuDayNightCycle;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Menu")
    EMenuState CurrentState = EMenuState::Title;

    void SpawnDayNightCycle();
};
