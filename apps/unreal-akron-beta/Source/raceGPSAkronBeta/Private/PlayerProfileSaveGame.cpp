// Copyright raceGPS. All Rights Reserved.

#include "PlayerProfileSaveGame.h"
#include "Kismet/GameplayStatics.h"

const FString UPlayerProfileSaveGame::SaveSlotName = TEXT("PlayerProfile");
const int32 UPlayerProfileSaveGame::SaveUserIndex = 0;
const int32 UPlayerProfileSaveGame::XPPerLevel = 1000;

UPlayerProfileSaveGame::UPlayerProfileSaveGame()
    : PlayerName(TEXT("Racer"))
    , PlayerLevel(1)
    , TotalXP(0)
    , TotalDistanceDriven(0.0f)
    , TotalRaces(0)
    , TotalWins(0)
{
}

bool UPlayerProfileSaveGame::SaveProfile()
{
    if (UGameplayStatics::SaveGameToSlot(this, SaveSlotName, SaveUserIndex))
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] PlayerProfile saved to slot %s"), *SaveSlotName);
        return true;
    }
    UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Failed to save PlayerProfile to slot %s"), *SaveSlotName);
    return false;
}

UPlayerProfileSaveGame* UPlayerProfileSaveGame::LoadProfile()
{
    USaveGame* Loaded = UGameplayStatics::LoadGameFromSlot(SaveSlotName, SaveUserIndex);
    if (UPlayerProfileSaveGame* Profile = Cast<UPlayerProfileSaveGame>(Loaded))
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] PlayerProfile loaded from slot %s"), *SaveSlotName);
        return Profile;
    }

    // No save found or cast failed (e.g., outdated version / corrupted data) — create a fresh default profile.
    UPlayerProfileSaveGame* NewProfile = NewObject<UPlayerProfileSaveGame>(
        GetTransientPackage(), UPlayerProfileSaveGame::StaticClass());
    if (NewProfile)
    {
        NewProfile->SaveProfile();
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Created default PlayerProfile in slot %s"), *SaveSlotName);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("[raceGPS] Failed to create default PlayerProfile"));
    }
    return NewProfile;
}

void UPlayerProfileSaveGame::AddXP(int32 Amount)
{
    if (Amount <= 0)
        return;

    TotalXP += Amount;
    CheckLevelUp();
    SaveProfile();
}

void UPlayerProfileSaveGame::CheckLevelUp()
{
    int32 NewLevel = (TotalXP / XPPerLevel) + 1;
    if (NewLevel > PlayerLevel)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Level up! %d -> %d"), PlayerLevel, NewLevel);
        PlayerLevel = NewLevel;
    }
}

void UPlayerProfileSaveGame::UnlockPart(const FString& PartId)
{
    if (PartId.IsEmpty() || UnlockedParts.Contains(PartId))
        return;
    UnlockedParts.Add(PartId);
    SaveProfile();
}

void UPlayerProfileSaveGame::UnlockMaterial(const FString& MaterialId)
{
    if (MaterialId.IsEmpty() || UnlockedMaterials.Contains(MaterialId))
        return;
    UnlockedMaterials.Add(MaterialId);
    SaveProfile();
}

void UPlayerProfileSaveGame::UnlockDecal(const FString& DecalId)
{
    if (DecalId.IsEmpty() || UnlockedDecals.Contains(DecalId))
        return;
    UnlockedDecals.Add(DecalId);
    SaveProfile();
}

void UPlayerProfileSaveGame::AddDistance(float Meters)
{
    if (Meters <= 0.0f)
        return;
    TotalDistanceDriven += Meters;
    SaveProfile();
}

void UPlayerProfileSaveGame::RecordRaceFinished(bool bWon, float LapTime, const FString& TrackId)
{
    TotalRaces++;
    if (bWon)
    {
        TotalWins++;
    }

    if (!TrackId.IsEmpty() && LapTime > 0.0f)
    {
        float* Existing = BestLapTimes.Find(TrackId);
        if (!Existing || LapTime < *Existing)
        {
            BestLapTimes.Add(TrackId, LapTime);
            UE_LOG(LogTemp, Log, TEXT("[raceGPS] New best lap on %s: %.2f"), *TrackId, LapTime);
        }
    }

    SaveProfile();
}

bool UPlayerProfileSaveGame::HasUnlockedPart(const FString& PartId) const
{
    return UnlockedParts.Contains(PartId);
}

bool UPlayerProfileSaveGame::HasUnlockedMaterial(const FString& MaterialId) const
{
    return UnlockedMaterials.Contains(MaterialId);
}

bool UPlayerProfileSaveGame::HasUnlockedDecal(const FString& DecalId) const
{
    return UnlockedDecals.Contains(DecalId);
}

float UPlayerProfileSaveGame::GetBestLapTime(const FString& TrackId) const
{
    const float* Existing = BestLapTimes.Find(TrackId);
    return Existing ? *Existing : -1.0f;
}
