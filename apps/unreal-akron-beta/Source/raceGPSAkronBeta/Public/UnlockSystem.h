// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "UnlockSystem.generated.h"

class UPlayerProfileSaveGame;

/**
 * Progress information for a single unlockable content item.
 */
USTRUCT(BlueprintType)
struct FUnlockProgress
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    FString ContentId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    bool bUnlocked = false;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    float ProgressPercent = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    FString NextRequirementText;
};

/**
 * Definition of how a piece of content is unlocked.
 */
USTRUCT(BlueprintType)
struct FUnlockDefinition
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    FString ContentId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    FString ContentType;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    int32 RequiredLevel = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    int32 RequiredRaces = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    float RequiredDriftMeters = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Unlocks")
    FString DisplayName;
};

/**
 * Tracks content unlocks based on player progression.
 * Unlock conditions are defined in JSON and evaluated against the player profile.
 */
UCLASS()
class RACEGPSAKRONBETA_API UUnlockSystem : public UObject
{
    GENERATED_BODY()

public:
    UUnlockSystem();

    /** Check whether a specific content ID is unlocked. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    bool IsUnlocked(const FString& ContentId) const;

    /**
     * Evaluate all definitions against the provided profile.
     * Returns an array of content IDs that were newly unlocked.
     */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    TArray<FString> CheckUnlockConditions(UPlayerProfileSaveGame* Profile);

    /** Get detailed progress for a single content ID. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    FUnlockProgress GetUnlockProgress(const FString& ContentId, UPlayerProfileSaveGame* Profile) const;

    /** Get all unlock definitions. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    TArray<FUnlockDefinition> GetAllDefinitions() const;

    /** Force unlock a content ID (e.g., for cheats or admin). */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    void ForceUnlock(const FString& ContentId);

    /** Save the current unlocked state to JSON. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    bool SaveUnlockState();

    /** Load the unlocked state from JSON. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Unlocks")
    bool LoadUnlockState();

protected:
    UPROPERTY()
    TArray<FUnlockDefinition> Definitions;

    UPROPERTY()
    TArray<FString> UnlockedIds;

    void LoadDefinitionsFromJson();
    void CreateDefaultDefinitions();

    FString GetUnlockStatePath() const;
    FString GetUnlockDefinitionsPath() const;
};
