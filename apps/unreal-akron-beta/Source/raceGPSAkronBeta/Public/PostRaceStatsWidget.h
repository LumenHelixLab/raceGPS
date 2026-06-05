#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "PostRaceStatsWidget.generated.h"

UCLASS()
class RACEGPSAKRONBETA_API UPostRaceStatsWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Stats")
    void ShowStats(float BaseTime, float PenaltyTime, float BonusTime, float FinalTime,
                   int32 Collisions, int32 MissedCPs, const FString& Medal,
                   float BestTime, int32 Rank);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Stats")
    void OnRestartClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Stats")
    void OnLeaderboardClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Stats")
    void OnMenuClicked();

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* FinalTimeText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* BaseTimeText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* PenaltyText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* BonusText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* CollisionsText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* MissedCPText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* MedalText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* BestTimeText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* RankText;

    UPROPERTY(meta = (BindWidget))
    class UButton* RestartButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* LeaderboardButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* MenuButton;
};
