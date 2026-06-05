#include "PostRaceStatsWidget.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"
#include "Kismet/GameplayStatics.h"
#include "CruiseSprintGameMode.h"

void UPostRaceStatsWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (RestartButton)
    {
        RestartButton->OnClicked.AddDynamic(this, &UPostRaceStatsWidget::OnRestartClicked);
    }
    if (LeaderboardButton)
    {
        LeaderboardButton->OnClicked.AddDynamic(this, &UPostRaceStatsWidget::OnLeaderboardClicked);
    }
    if (MenuButton)
    {
        MenuButton->OnClicked.AddDynamic(this, &UPostRaceStatsWidget::OnMenuClicked);
    }
}

void UPostRaceStatsWidget::ShowStats(float BaseTime, float PenaltyTime, float BonusTime, float FinalTime,
                                      int32 Collisions, int32 MissedCPs, const FString& Medal,
                                      float BestTime, int32 Rank)
{
    auto Format = [](float Seconds) -> FString
    {
        int32 M = FMath::FloorToInt(Seconds / 60.0f);
        int32 S = FMath::FloorToInt(Seconds) % 60;
        int32 MS = FMath::FloorToInt((Seconds - FMath::FloorToInt(Seconds)) * 1000.0f);
        return FString::Printf(TEXT("%02d:%02d.%03d"), M, S, MS);
    };

    if (FinalTimeText) FinalTimeText->SetText(FText::FromString(Format(FinalTime)));
    if (BaseTimeText) BaseTimeText->SetText(FText::FromString(FString::Printf(TEXT("Base: %s"), *Format(BaseTime))));
    if (PenaltyText) PenaltyText->SetText(FText::FromString(FString::Printf(TEXT("Penalties: +%s"), *Format(PenaltyTime))));
    if (BonusText) BonusText->SetText(FText::FromString(FString::Printf(TEXT("Bonus: -%s"), *Format(BonusTime))));
    if (CollisionsText) CollisionsText->SetText(FText::FromString(FString::Printf(TEXT("Collisions: %d"), Collisions)));
    if (MissedCPText) MissedCPText->SetText(FText::FromString(FString::Printf(TEXT("Missed Checkpoints: %d"), MissedCPs)));
    if (MedalText) MedalText->SetText(FText::FromString(Medal));
    if (BestTimeText) BestTimeText->SetText(FText::FromString(FString::Printf(TEXT("Best: %s"), *Format(BestTime))));
    if (RankText) RankText->SetText(FText::FromString(FString::Printf(TEXT("Rank: #%d"), Rank)));
}

void UPostRaceStatsWidget::OnRestartClicked()
{
    ACruiseSprintGameMode* GM = Cast<ACruiseSprintGameMode>(UGameplayStatics::GetGameMode(GetWorld()));
    if (GM)
    {
        GM->RestartRace();
    }
    RemoveFromParent();
}

void UPostRaceStatsWidget::OnLeaderboardClicked()
{
    // TODO: Show leaderboard widget
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Leaderboard button clicked"));
}

void UPostRaceStatsWidget::OnMenuClicked()
{
    UGameplayStatics::OpenLevel(GetWorld(), FName(TEXT("MainMenu")));
    RemoveFromParent();
}
