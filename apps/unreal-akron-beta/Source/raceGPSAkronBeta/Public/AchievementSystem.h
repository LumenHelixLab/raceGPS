#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "AchievementSystem.generated.h"

USTRUCT(BlueprintType)
struct FAchievement
{
    GENERATED_BODY()

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Id;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Title;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString Description;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FString IconPath;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    int32 ProgressTarget = 1;

    UPROPERTY(BlueprintReadOnly)
    int32 CurrentProgress = 0;

    UPROPERTY(BlueprintReadOnly)
    bool bUnlocked = false;

    UPROPERTY(BlueprintReadOnly)
    FString UnlockDate;
};

UCLASS()
class RACEGPSAKRONBETA_API UAchievementSystem : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    void InitializeAchievements();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    void UnlockAchievement(const FString& AchievementId);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    void AddProgress(const FString& AchievementId, int32 Amount = 1);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    bool IsUnlocked(const FString& AchievementId) const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    TArray<FAchievement> GetAllAchievements() const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    bool SaveAchievements();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Achievements")
    bool LoadAchievements();

protected:
    UPROPERTY()
    TMap<FString, FAchievement> Achievements;

    FString GetAchievementsPath() const;
};
