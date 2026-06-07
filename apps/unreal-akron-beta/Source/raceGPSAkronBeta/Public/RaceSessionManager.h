// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "RaceSessionManager.generated.h"

UENUM(BlueprintType)
enum class ERaceSessionState : uint8
{
    Menu        UMETA(DisplayName = "Menu"),
    Countdown   UMETA(DisplayName = "Countdown"),
    Racing      UMETA(DisplayName = "Racing"),
    Paused      UMETA(DisplayName = "Paused"),
    Finished    UMETA(DisplayName = "Finished")
};

USTRUCT(BlueprintType)
struct FRaceResults
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    FString TrackId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    float FinalTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    float BestLapTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    float TotalDriftScore = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    int32 CurrentCheckpoint = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    int32 TotalCheckpoints = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    int32 EarnedXP = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    FString Medal;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceResults")
    TArray<FString> UnlocksGranted;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnRaceSessionStateChanged, ERaceSessionState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnRaceFinished, FRaceResults, Results);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCheckpointPassed, int32, CheckpointIndex);

/**
 * Singleton-like manager that orchestrates a single race session.
 * Handles countdown, racing, pausing, checkpoint tracking, reward calculation,
 * and end-screen dispatch.
 */
UCLASS()
class RACEGPSAKRONBETA_API URaceSessionManager : public UObject
{
    GENERATED_BODY()

public:
    /** Get or create the singleton RaceSessionManager for the current world. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession", meta = (WorldContext = "WorldContextObject"))
    static URaceSessionManager* GetInstance(UObject* WorldContextObject);

    /** Configure a new session. Does not start racing yet. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void StartSession(const FString& TrackId, const FString& CarBuildId);

    /** Begin the race countdown and then transition to Racing. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void StartRace();

    /** Pause an active race. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void PauseRace();

    /** Resume a paused race. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void ResumeRace();

    /** End the race immediately, calculate rewards, and show the end screen. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void EndRace();

    /** Get current race session state. */
    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceSession")
    ERaceSessionState GetCurrentState() const { return CurrentState; }

    /** Tick the session (countdown, timing). Should be called by the owning GameMode each frame. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void TickSession(float DeltaTime);

    /** Called when the player passes a checkpoint. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void OnCheckpointReached(int32 CheckpointIndex);

    /** Set the vehicle tuning data to apply when the race starts. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceSession")
    void SetVehicleTuningData(class UVehicleTuningData* TuningData);

    UPROPERTY(BlueprintAssignable, Category = "raceGPS|RaceSession")
    FOnRaceSessionStateChanged OnStateChanged;

    UPROPERTY(BlueprintAssignable, Category = "raceGPS|RaceSession")
    FOnRaceFinished OnRaceFinished;

    UPROPERTY(BlueprintAssignable, Category = "raceGPS|RaceSession")
    FOnCheckpointPassed OnCheckpointPassed;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    FString CurrentTrackId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    FString CurrentCarBuildId;

    UPROPERTY(BlueprintReadWrite, Category = "raceGPS|RaceSession")
    int32 TotalCheckpoints = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    int32 CurrentCheckpoint = 0;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float CountdownDuration = 3.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float GoldTimeSeconds = 120.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float SilverTimeSeconds = 150.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float BronzeTimeSeconds = 200.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float ElapsedTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    float CountdownTimer = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    TObjectPtr<class URaceTimerSystem> RaceTimer;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    TObjectPtr<class UDriftScoreSystem> DriftSystem;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceSession")
    TObjectPtr<class UGhostVehicleSystem> GhostSystem;

protected:
    UPROPERTY()
    ERaceSessionState CurrentState = ERaceSessionState::Menu;

    UPROPERTY()
    TObjectPtr<class UVehicleTuningData> SelectedVehicleTuning;

    UPROPERTY()
    TObjectPtr<class UPlayerProfileSaveGame> ActiveProfile;

    void SetState(ERaceSessionState NewState);
    void UpdateCountdown(float DeltaTime);
    void InitializeSystems();
    void SpawnPlayerVehicle();
    void CalculateRewards(FRaceResults& OutResults);
    void ShowEndScreen(const FRaceResults& Results);
    FString CalculateMedal(float TimeSeconds) const;

    float DriftScoreAtFinish = 0.0f;
};
