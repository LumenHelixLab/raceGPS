#include "RaceLoopHarness.h"
#include "LeaderboardSystem.h"
#include "LeaderboardEntry.h"
#include "RaceReplayManager.h"

void URaceLoopHarness::BindScoringSystem(URaceScoringSystem* InScoring)
{
    ScoringSystem = InScoring;
}

void URaceLoopHarness::BindLeaderboardSystem(ULeaderboardSystem* InLeaderboard)
{
    LeaderboardSystem = InLeaderboard;
}

void URaceLoopHarness::BindReplayManager(URaceReplayManager* InReplay)
{
    ReplayManager = InReplay;
}

void URaceLoopHarness::SetMedalTimes(float GoldSeconds, float SilverSeconds, float BronzeSeconds)
{
    GoldTimeSeconds = GoldSeconds;
    SilverTimeSeconds = SilverSeconds;
    BronzeTimeSeconds = BronzeSeconds;
}

void URaceLoopHarness::InstallPlaceholderCourse()
{
    // Straight 50m sprint in UE cm. Not a closed loop; no speed/collision gate.
    TArray<FVector> PlaceholderWaypoints;
    PlaceholderWaypoints.Add(FVector(0.0f, 0.0f, 50.0f));
    PlaceholderWaypoints.Add(FVector(2500.0f, 0.0f, 50.0f));
    PlaceholderWaypoints.Add(FVector(5000.0f, 0.0f, 50.0f));

    TArray<FVector> PlaceholderCheckpoints;
    PlaceholderCheckpoints.Add(FVector(2500.0f, 0.0f, 100.0f));
    PlaceholderCheckpoints.Add(FVector(5000.0f, 0.0f, 100.0f));

    InstallCourse(
        PlaceholderRouteId(),
        FVector(0.0f, 0.0f, 50.0f),
        FRotator::ZeroRotator,
        PlaceholderWaypoints,
        PlaceholderCheckpoints,
        50.0f);

    bPlaceholderCourse = true;

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Placeholder course installed: route=%s waypoints=%d checkpoints=%d"),
        *RouteId, Waypoints.Num(), CheckpointLocations.Num());
}

void URaceLoopHarness::InstallCourse(
    const FString& InRouteId,
    const FVector& SpawnLocation,
    const FRotator& SpawnRotation,
    const TArray<FVector>& InWaypoints,
    const TArray<FVector>& InCheckpoints,
    float DistanceMeters)
{
    RouteId = InRouteId;
    PlayerSpawnLocation = SpawnLocation;
    PlayerSpawnRotation = SpawnRotation;
    Waypoints = InWaypoints;
    CheckpointLocations = InCheckpoints;
    TotalDistanceMeters = DistanceMeters;
    bPlaceholderCourse = false;
    bCourseInstalled = true;
    CurrentCheckpoint = 0;
}

void URaceLoopHarness::BeginLoading()
{
    State = ECruiseSprintState::Loading;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
        *UEnum::GetValueAsString(State));
}

void URaceLoopHarness::CompleteLoading()
{
    if (State != ECruiseSprintState::Loading && State != ECruiseSprintState::None)
    {
        return;
    }

    State = ECruiseSprintState::Countdown;
    CountdownTimer = CountdownDuration;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
        *UEnum::GetValueAsString(State));
}

void URaceLoopHarness::ResetRunState()
{
    ElapsedTime = 0.0f;
    CurrentCheckpoint = 0;
    LastScore = FRaceScore();
    if (URaceScoringSystem* Scoring = GetScoringSystem())
    {
        Scoring->Reset();
    }
}

void URaceLoopHarness::StartRace()
{
    ResetRunState();
    State = ECruiseSprintState::Countdown;
    CountdownTimer = CountdownDuration;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
        *UEnum::GetValueAsString(State));
}

void URaceLoopHarness::RestartRace()
{
    StartRace();
}

void URaceLoopHarness::PauseRace()
{
    if (State == ECruiseSprintState::Racing)
    {
        State = ECruiseSprintState::Paused;
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
            *UEnum::GetValueAsString(State));
    }
}

void URaceLoopHarness::ResumeRace()
{
    if (State == ECruiseSprintState::Paused)
    {
        State = ECruiseSprintState::Racing;
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
            *UEnum::GetValueAsString(State));
    }
}

void URaceLoopHarness::TickLoop(float DeltaTime)
{
    if (State == ECruiseSprintState::Countdown)
    {
        CountdownTimer -= DeltaTime;
        if (CountdownTimer <= 0.0f)
        {
            CountdownTimer = 0.0f;
            State = ECruiseSprintState::Racing;
            ElapsedTime = 0.0f;
            CurrentCheckpoint = 0;
            UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
                *UEnum::GetValueAsString(State));
        }
    }
    else if (State == ECruiseSprintState::Racing)
    {
        ElapsedTime += DeltaTime;
    }
}

bool URaceLoopHarness::OnCheckpointReached(int32 CheckpointIndex)
{
    if (State != ECruiseSprintState::Racing)
    {
        return false;
    }

    if (CheckpointIndex != CurrentCheckpoint)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Out-of-order checkpoint %d ignored (expected %d)"),
            CheckpointIndex, CurrentCheckpoint);
        return false;
    }

    CurrentCheckpoint++;
    if (URaceScoringSystem* Scoring = GetScoringSystem())
    {
        Scoring->OnCheckpointReached();
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Checkpoint %d reached"), CheckpointIndex);

    if (GetTotalCheckpoints() > 0 && CurrentCheckpoint >= GetTotalCheckpoints())
    {
        FinishRace();
    }

    return true;
}

void URaceLoopHarness::FinishRace()
{
    if (State == ECruiseSprintState::Finished)
    {
        return;
    }

    State = ECruiseSprintState::Finished;

    if (URaceScoringSystem* Scoring = GetScoringSystem())
    {
        LastScore = Scoring->CalculateFinalScore(ElapsedTime);
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race finished! Base: %.2fs, Penalties: %.2fs, Bonus: %.2fs, Final: %.2fs, Medal: %s"),
            LastScore.BaseTime,
            LastScore.CollisionPenalty + LastScore.MissedCheckpointPenalty,
            LastScore.CleanDrivingBonus,
            LastScore.FinalTime,
            *LastScore.Medal);
    }

    WriteLeaderboardEntry();

    if (ReplayManager)
    {
        ReplayManager->EndRaceRecording();
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Race state changed to: %s"),
        *UEnum::GetValueAsString(State));
}

URaceScoringSystem* URaceLoopHarness::GetScoringSystem()
{
    if (!ScoringSystem)
    {
        ScoringSystem = NewObject<URaceScoringSystem>(this);
    }
    return ScoringSystem;
}

void URaceLoopHarness::WriteLeaderboardEntry()
{
    if (!LeaderboardSystem || RouteId.IsEmpty())
    {
        return;
    }

    if (!LeaderboardSystem->HasLeaderboard(RouteId))
    {
        LeaderboardSystem->SeedDefaultEntries(RouteId, GoldTimeSeconds, SilverTimeSeconds, BronzeTimeSeconds);
    }

    FLeaderboardEntry Entry;
    Entry.PlayerName = TEXT("Player");
    Entry.TimeSeconds = LastScore.FinalTime;
    Entry.Medal = LastScore.Medal;
    Entry.Date = FDateTime::Now().ToString(TEXT("%Y-%m-%d"));
    Entry.VehicleUsed = TEXT("Sedan");
    Entry.Collisions = LastScore.Collisions;
    Entry.bIsPlayer = true;
    LeaderboardSystem->AddEntry(RouteId, Entry);
}
