// Copyright LumenHelix Solutions. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Misc/Paths.h"
#include "RaceScoringSystem.h"
#include "AchievementSystem.h"
#include "LeaderboardSystem.h"
#include "VehicleTuningData.h"
#include "RaceLoopHarness.h"

// ---------------------------------------------------------------------------
// Race Scoring Tests
// ---------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSScoringPerfectRun, "raceGPS.Gameplay.Scoring.PerfectRun",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSScoringPerfectRun::RunTest(const FString& Parameters)
{
    URaceScoringSystem* Scoring = NewObject<URaceScoringSystem>();
    Scoring->Reset();

    // Simulate a 110s race with 0 collisions, 0 missed checkpoints
    Scoring->BaseTime = 110.0f;
    Scoring->Collisions = 0;
    Scoring->MissedCheckpoints = 0;

    FRaceScore Score = Scoring->CalculateFinalScore(110.0f);

    TestEqual(TEXT("Base time should be 110"), Score.BaseTime, 110.0f);
    TestEqual(TEXT("Collision penalty should be 0"), Score.CollisionPenalty, 0.0f);
    TestEqual(TEXT("Clean bonus should be -1.0"), Score.CleanDrivingBonus, -1.0f);
    TestEqual(TEXT("Final time should be 109.0"), Score.FinalTime, 109.0f);
    TestEqual(TEXT("Medal should be GOLD"), Score.Medal, FString(TEXT("GOLD")));

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSScoringMessyRun, "raceGPS.Gameplay.Scoring.MessyRun",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSScoringMessyRun::RunTest(const FString& Parameters)
{
    URaceScoringSystem* Scoring = NewObject<URaceScoringSystem>();
    Scoring->Reset();

    Scoring->BaseTime = 100.0f;
    Scoring->Collisions = 3;
    Scoring->MissedCheckpoints = 1;

    FRaceScore Score = Scoring->CalculateFinalScore(100.0f);

    // 100 + (3 * 2) + (1 * 5) - 0 = 111
    TestEqual(TEXT("Final time should be 111.0"), Score.FinalTime, 111.0f);
    TestEqual(TEXT("Collision penalty should be 6.0"), Score.CollisionPenalty, 6.0f);
    TestEqual(TEXT("Missed CP penalty should be 5.0"), Score.MissedCheckpointPenalty, 5.0f);
    TestEqual(TEXT("Clean bonus should be 0"), Score.CleanDrivingBonus, 0.0f);

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSScoringMedalBoundaries, "raceGPS.Gameplay.Scoring.MedalBoundaries",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSScoringMedalBoundaries::RunTest(const FString& Parameters)
{
    URaceScoringSystem* Scoring = NewObject<URaceScoringSystem>();
    Scoring->Reset();

    // Gold boundary
    Scoring->Collisions = 0;
    Scoring->MissedCheckpoints = 0;
    FRaceScore Score = Scoring->CalculateFinalScore(120.0f);
    TestEqual(TEXT("120s clean should be GOLD"), Score.Medal, FString(TEXT("GOLD")));

    // Silver boundary
    Scoring->Reset();
    Scoring->Collisions = 0;
    Scoring->MissedCheckpoints = 0;
    Score = Scoring->CalculateFinalScore(150.0f);
    TestEqual(TEXT("150s clean should be SILVER"), Score.Medal, FString(TEXT("SILVER")));

    // Bronze boundary
    Scoring->Reset();
    Scoring->Collisions = 0;
    Scoring->MissedCheckpoints = 0;
    Score = Scoring->CalculateFinalScore(200.0f);
    TestEqual(TEXT("200s clean should be BRONZE"), Score.Medal, FString(TEXT("BRONZE")));

    // No medal
    Scoring->Reset();
    Scoring->Collisions = 0;
    Scoring->MissedCheckpoints = 0;
    Score = Scoring->CalculateFinalScore(201.0f);
    TestEqual(TEXT("201s clean should be NONE"), Score.Medal, FString(TEXT("NONE")));

    return true;
}

// ---------------------------------------------------------------------------
// Achievement Tests
// ---------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSAchievementUnlock, "raceGPS.Gameplay.Achievements.Unlock",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSAchievementUnlock::RunTest(const FString& Parameters)
{
    UAchievementSystem* Achievements = NewObject<UAchievementSystem>();
    Achievements->InitializeAchievements();

    TestFalse(TEXT("first_race should start locked"), Achievements->IsUnlocked(TEXT("first_race")));

    Achievements->UnlockAchievement(TEXT("first_race"));
    TestTrue(TEXT("first_race should be unlocked after UnlockAchievement"), Achievements->IsUnlocked(TEXT("first_race")));

    // Double-unlock should be safe
    Achievements->UnlockAchievement(TEXT("first_race"));
    TestTrue(TEXT("first_race should still be unlocked"), Achievements->IsUnlocked(TEXT("first_race")));

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSAchievementProgress, "raceGPS.Gameplay.Achievements.Progress",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSAchievementProgress::RunTest(const FString& Parameters)
{
    UAchievementSystem* Achievements = NewObject<UAchievementSystem>();
    Achievements->InitializeAchievements();

    // gold_medalist requires 3 progress
    Achievements->AddProgress(TEXT("gold_medalist"), 1);
    TestFalse(TEXT("gold_medalist should be locked at 1/3"), Achievements->IsUnlocked(TEXT("gold_medalist")));

    Achievements->AddProgress(TEXT("gold_medalist"), 1);
    TestFalse(TEXT("gold_medalist should be locked at 2/3"), Achievements->IsUnlocked(TEXT("gold_medalist")));

    Achievements->AddProgress(TEXT("gold_medalist"), 1);
    TestTrue(TEXT("gold_medalist should unlock at 3/3"), Achievements->IsUnlocked(TEXT("gold_medalist")));

    return true;
}

// ---------------------------------------------------------------------------
// Leaderboard Tests
// ---------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSLeaderboardAddAndSort, "raceGPS.Gameplay.Leaderboard.AddAndSort",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSLeaderboardAddAndSort::RunTest(const FString& Parameters)
{
    ULeaderboardSystem* Leaderboards = NewObject<ULeaderboardSystem>();
    FString RouteId = TEXT("test_route");

    Leaderboards->SeedDefaultEntries(RouteId, 120.0f, 150.0f, 200.0f);

    // Add a player entry
    FLeaderboardEntry Entry;
    Entry.PlayerName = TEXT("Player");
    Entry.TimeSeconds = 130.0f;
    Entry.Medal = TEXT("SILVER");
    Entry.Date = TEXT("2026-06-04");
    Entry.VehicleUsed = TEXT("Sedan");
    Entry.Collisions = 1;
    Entry.bIsPlayer = true;
    Leaderboards->AddEntry(RouteId, Entry);

    TArray<FLeaderboardEntry> Entries = Leaderboards->GetEntries(RouteId);
    TestTrue(TEXT("Leaderboard should have entries"), Entries.Num() > 0);

    // Player at 130s should rank below Gold (120s) but above Silver AI
    int32 Rank = Leaderboards->GetPlayerRank(RouteId, 130.0f);
    TestEqual(TEXT("Player rank at 130s should be 2 (below Gold)"), Rank, 2);

    return true;
}

// ---------------------------------------------------------------------------
// Vehicle Tuning Tests
// ---------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSVehicleTuningPreset, "raceGPS.Gameplay.Vehicle.TuningPreset",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSVehicleTuningPreset::RunTest(const FString& Parameters)
{
    UVehicleTuningData* Tuning = NewObject<UVehicleTuningData>();
    Tuning->DisplayName = TEXT("Test Vehicle");
    Tuning->Description = TEXT("A test vehicle for validation.");
    Tuning->VehicleClass = EVehicleClass::Sports;
    Tuning->VehicleMass = 1200.0f;
    Tuning->MaxEngineRPM = 8000.0f;

    TestEqual(TEXT("Display name should match"), Tuning->DisplayName, FString(TEXT("Test Vehicle")));
    TestEqual(TEXT("Vehicle class should be Sports"), static_cast<uint8>(Tuning->VehicleClass), static_cast<uint8>(EVehicleClass::Sports));
    TestEqual(TEXT("Mass should be 1200"), Tuning->VehicleMass, 1200.0f);

    return true;
}

// ---------------------------------------------------------------------------
// Placeholder race-loop tests (no world / PIE required)
// ---------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSRaceLoopPlaceholderCheckpoints, "raceGPS.Gameplay.RaceLoop.PlaceholderCheckpoints",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSRaceLoopPlaceholderCheckpoints::RunTest(const FString& Parameters)
{
    URaceLoopHarness* Loop = NewObject<URaceLoopHarness>();
    Loop->InstallPlaceholderCourse();

    TestTrue(TEXT("Placeholder course is marked installed"), Loop->HasCourse());
    TestTrue(TEXT("Placeholder course flag is set"), Loop->IsPlaceholderCourse());
    TestEqual(TEXT("Route id is placeholder_sprint"), Loop->GetRouteId(), FString(TEXT("placeholder_sprint")));
    TestTrue(TEXT("GetTotalCheckpoints() > 0 on placeholder"), Loop->GetTotalCheckpoints() > 0);
    TestTrue(TEXT("At least 2 waypoints"), Loop->GetWaypoints().Num() >= 2);
    TestTrue(TEXT("At least 2 checkpoint gates"), Loop->GetCheckpointLocations().Num() >= 2);
    TestEqual(TEXT("Checkpoint count matches locations"), Loop->GetTotalCheckpoints(), Loop->GetCheckpointLocations().Num());

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSRaceLoopCountdownToRacing, "raceGPS.Gameplay.RaceLoop.CountdownToRacing",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSRaceLoopCountdownToRacing::RunTest(const FString& Parameters)
{
    URaceLoopHarness* Loop = NewObject<URaceLoopHarness>();
    Loop->InstallPlaceholderCourse();
    Loop->CountdownDuration = 1.0f;

    Loop->BeginLoading();
    TestTrue(TEXT("BeginLoading enters Loading"), Loop->GetState() == ECruiseSprintState::Loading);

    Loop->CompleteLoading();
    TestTrue(TEXT("CompleteLoading enters Countdown"), Loop->GetState() == ECruiseSprintState::Countdown);

    Loop->StartRace();
    TestTrue(TEXT("StartRace enters Countdown"), Loop->GetState() == ECruiseSprintState::Countdown);

    Loop->TickLoop(0.4f);
    TestTrue(TEXT("Countdown still running before expiry"), Loop->GetState() == ECruiseSprintState::Countdown);

    Loop->TickLoop(0.7f);
    TestTrue(TEXT("Countdown expiry enters Racing"), Loop->GetState() == ECruiseSprintState::Racing);
    TestEqual(TEXT("Checkpoint index resets at race start"), Loop->GetCurrentCheckpoint(), 0);
    TestEqual(TEXT("Elapsed time resets at race start"), Loop->GetElapsedTime(), 0.0f);

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSRaceLoopInOrderFinish, "raceGPS.Gameplay.RaceLoop.InOrderFinish",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSRaceLoopInOrderFinish::RunTest(const FString& Parameters)
{
    URaceLoopHarness* Loop = NewObject<URaceLoopHarness>();
    URaceScoringSystem* Scoring = NewObject<URaceScoringSystem>(Loop);
    ULeaderboardSystem* Board = NewObject<ULeaderboardSystem>(Loop);
    Loop->BindScoringSystem(Scoring);
    Loop->BindLeaderboardSystem(Board);
    Loop->InstallPlaceholderCourse();
    Loop->CountdownDuration = 0.1f;

    Loop->StartRace();
    Loop->TickLoop(0.2f);
    TestTrue(TEXT("In Racing before checkpoints"), Loop->GetState() == ECruiseSprintState::Racing);

    Loop->TickLoop(8.0f);

    const int32 Total = Loop->GetTotalCheckpoints();
    for (int32 Index = 0; Index < Total; ++Index)
    {
        const bool bAccepted = Loop->OnCheckpointReached(Index);
        const FString Message = FString::Printf(TEXT("In-order checkpoint %d accepted"), Index);
        TestTrue(*Message, bAccepted);
    }

    TestTrue(TEXT("Last checkpoint finishes the race"), Loop->GetState() == ECruiseSprintState::Finished);
    TestEqual(TEXT("CurrentCheckpoint equals total"), Loop->GetCurrentCheckpoint(), Total);

    const FRaceScore LastScore = Loop->GetLastScore();
    TestTrue(TEXT("Harness stored a final score"), LastScore.BaseTime > 0.0f);

    const FRaceScore ScoringScore = Scoring->CalculateFinalScore(Loop->GetElapsedTime());
    TestEqual(TEXT("ScoringSystem final time matches harness"), LastScore.FinalTime, ScoringScore.FinalTime);

    TestTrue(TEXT("Leaderboard written for placeholder_sprint"),
        Board->HasLeaderboard(URaceLoopHarness::PlaceholderRouteId()));

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSRaceLoopOutOfOrderIgnored, "raceGPS.Gameplay.RaceLoop.OutOfOrderIgnored",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSRaceLoopOutOfOrderIgnored::RunTest(const FString& Parameters)
{
    URaceLoopHarness* Loop = NewObject<URaceLoopHarness>();
    Loop->InstallPlaceholderCourse();
    Loop->CountdownDuration = 0.1f;
    Loop->StartRace();
    Loop->TickLoop(0.2f);

    TestTrue(TEXT("Need at least two gates to test order"), Loop->GetTotalCheckpoints() >= 2);

    const bool bSkip = Loop->OnCheckpointReached(1);
    TestFalse(TEXT("Out-of-order checkpoint is ignored"), bSkip);
    TestEqual(TEXT("CurrentCheckpoint unchanged after out-of-order"), Loop->GetCurrentCheckpoint(), 0);
    TestTrue(TEXT("Still Racing after out-of-order"), Loop->GetState() == ECruiseSprintState::Racing);

    TestTrue(TEXT("Expected first gate still accepted"), Loop->OnCheckpointReached(0));
    TestEqual(TEXT("Advanced to checkpoint 1"), Loop->GetCurrentCheckpoint(), 1);
    TestTrue(TEXT("Still Racing after first gate"), Loop->GetState() == ECruiseSprintState::Racing);

    return true;
}
