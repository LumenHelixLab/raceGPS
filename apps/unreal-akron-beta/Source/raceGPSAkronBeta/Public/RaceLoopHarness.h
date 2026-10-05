#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "RaceScoringSystem.h"
#include "RaceLoopHarness.generated.h"

class ULeaderboardSystem;
class URaceReplayManager;

UENUM(BlueprintType)
enum class ECruiseSprintState : uint8
{
    None            UMETA(Hidden),
    Loading         UMETA(DisplayName = "Loading"),
    Countdown       UMETA(DisplayName = "Countdown"),
    Racing          UMETA(DisplayName = "Racing"),
    Finished        UMETA(DisplayName = "Finished"),
    Paused          UMETA(DisplayName = "Paused")
};

/**
 * World-independent Cruise Sprint loop: course install, countdown, in-order
 * checkpoints, scoring, leaderboard, replay end. ACruiseSprintGameMode owns
 * and calls this so the loop is real, not a dead harness.
 */
UCLASS()
class RACEGPSAKRONBETA_API URaceLoopHarness : public UObject
{
    GENERATED_BODY()

public:
    static FString PlaceholderRouteId() { return TEXT("placeholder_sprint"); }

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void BindScoringSystem(URaceScoringSystem* InScoring);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void BindLeaderboardSystem(ULeaderboardSystem* InLeaderboard);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void BindReplayManager(URaceReplayManager* InReplay);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void SetMedalTimes(float GoldSeconds, float SilverSeconds, float BronzeSeconds);

    /** Short straight sprint in UE centimeters. Not a loop. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void InstallPlaceholderCourse();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void InstallCourse(
        const FString& InRouteId,
        const FVector& SpawnLocation,
        const FRotator& SpawnRotation,
        const TArray<FVector>& InWaypoints,
        const TArray<FVector>& InCheckpoints,
        float DistanceMeters);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void BeginLoading();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void CompleteLoading();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void StartRace();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void RestartRace();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void PauseRace();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void ResumeRace();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void TickLoop(float DeltaTime);

    /** Returns true if this index was the expected next checkpoint. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    bool OnCheckpointReached(int32 CheckpointIndex);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    void FinishRace();

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    ECruiseSprintState GetState() const { return State; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    int32 GetCurrentCheckpoint() const { return CurrentCheckpoint; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    int32 GetTotalCheckpoints() const { return CheckpointLocations.Num(); }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    float GetElapsedTime() const { return ElapsedTime; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    float GetCountdownTimer() const { return CountdownTimer; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    FString GetRouteId() const { return RouteId; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    FRaceScore GetLastScore() const { return LastScore; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    bool IsPlaceholderCourse() const { return bPlaceholderCourse; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    bool HasCourse() const { return bCourseInstalled; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    FVector GetPlayerSpawnLocation() const { return PlayerSpawnLocation; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    FRotator GetPlayerSpawnRotation() const { return PlayerSpawnRotation; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|RaceLoop")
    float GetTotalDistanceMeters() const { return TotalDistanceMeters; }

    UFUNCTION(BlueprintCallable, Category = "raceGPS|RaceLoop")
    URaceScoringSystem* GetScoringSystem();

    const TArray<FVector>& GetWaypoints() const { return Waypoints; }
    const TArray<FVector>& GetCheckpointLocations() const { return CheckpointLocations; }

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|RaceLoop")
    float CountdownDuration = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|RaceLoop")
    float GoldTimeSeconds = 120.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|RaceLoop")
    float SilverTimeSeconds = 150.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|RaceLoop")
    float BronzeTimeSeconds = 200.0f;

protected:
    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    ECruiseSprintState State = ECruiseSprintState::None;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    float ElapsedTime = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    int32 CurrentCheckpoint = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    float CountdownTimer = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    FString RouteId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    FVector PlayerSpawnLocation = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    FRotator PlayerSpawnRotation = FRotator::ZeroRotator;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    TArray<FVector> Waypoints;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    TArray<FVector> CheckpointLocations;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    float TotalDistanceMeters = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    bool bPlaceholderCourse = false;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|RaceLoop")
    bool bCourseInstalled = false;

    UPROPERTY()
    TObjectPtr<URaceScoringSystem> ScoringSystem;

    UPROPERTY()
    TObjectPtr<ULeaderboardSystem> LeaderboardSystem;

    UPROPERTY()
    TObjectPtr<URaceReplayManager> ReplayManager;

    UPROPERTY()
    FRaceScore LastScore;

    void ResetRunState();
    void WriteLeaderboardEntry();
};
