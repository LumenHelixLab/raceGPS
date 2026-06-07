// Copyright raceGPS. All Rights Reserved.

#include "UnlockSystem.h"
#include "PlayerProfileSaveGame.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

UUnlockSystem::UUnlockSystem()
{
    LoadDefinitionsFromJson();
}

void UUnlockSystem::CreateDefaultDefinitions()
{
    auto Add = [&](const FString& Id, const FString& Type, int32 Level, int32 Races, float Drift, const FString& Name)
    {
        FUnlockDefinition Def;
        Def.ContentId = Id;
        Def.ContentType = Type;
        Def.RequiredLevel = Level;
        Def.RequiredRaces = Races;
        Def.RequiredDriftMeters = Drift;
        Def.DisplayName = Name;
        Definitions.Add(Def);
    };

    Add(TEXT("part_spoiler_01"),   TEXT("part"),     2, 0,    0.0f,   TEXT("Street Spoiler"));
    Add(TEXT("part_spoiler_02"),   TEXT("part"),     5, 5,    0.0f,   TEXT("Carbon Wing"));
    Add(TEXT("part_exhaust_01"),   TEXT("part"),     3, 0,    0.0f,   TEXT("Sport Exhaust"));
    Add(TEXT("material_neon_red"), TEXT("material"),  4, 0,    500.0f, TEXT("Neon Red Paint"));
    Add(TEXT("material_metal_blue"),TEXT("material"), 6, 10,   0.0f,   TEXT("Metallic Blue"));
    Add(TEXT("decal_flame_01"),    TEXT("decal"),    3, 0,    1000.0f,TEXT("Flame Decal"));
    Add(TEXT("decal_stripe_01"),   TEXT("decal"),    7, 20,   0.0f,   TEXT("Racing Stripes"));
}

void UUnlockSystem::LoadDefinitionsFromJson()
{
    FString Content;
    if (FFileHelper::LoadFileToString(Content, *GetUnlockDefinitionsPath()))
    {
        TSharedPtr<FJsonObject> Root;
        TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
        if (FJsonSerializer::Deserialize(Reader, Root))
        {
            const TArray<TSharedPtr<FJsonValue>>* Arr;
            if (Root->TryGetArrayField(TEXT("definitions"), Arr))
            {
                Definitions.Empty();
                for (const auto& Val : *Arr)
                {
                    const TSharedPtr<FJsonObject>* Obj;
                    if (!Val->TryGetObject(Obj))
                        continue;

                    FUnlockDefinition Def;
                    (*Obj)->TryGetStringField(TEXT("content_id"), Def.ContentId);
                    (*Obj)->TryGetStringField(TEXT("content_type"), Def.ContentType);
                    (*Obj)->TryGetNumberField(TEXT("required_level"), Def.RequiredLevel);
                    (*Obj)->TryGetNumberField(TEXT("required_races"), Def.RequiredRaces);
                    double Drift = 0.0;
                    if ((*Obj)->TryGetNumberField(TEXT("required_drift_meters"), Drift))
                    {
                        Def.RequiredDriftMeters = static_cast<float>(Drift);
                    }
                    (*Obj)->TryGetStringField(TEXT("display_name"), Def.DisplayName);
                    Definitions.Add(Def);
                }
                UE_LOG(LogTemp, Log, TEXT("[raceGPS] Loaded %d unlock definitions from JSON"), Definitions.Num());
                return;
            }
        }
    }

    // File missing or corrupted — fall back to hardcoded defaults.
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] No valid unlock_definitions.json found; using defaults"));
    CreateDefaultDefinitions();
}

bool UUnlockSystem::IsUnlocked(const FString& ContentId) const
{
    return UnlockedIds.Contains(ContentId);
}

TArray<FString> UUnlockSystem::CheckUnlockConditions(UPlayerProfileSaveGame* Profile)
{
    TArray<FString> NewlyUnlocked;
    if (!Profile)
        return NewlyUnlocked;

    for (const FUnlockDefinition& Def : Definitions)
    {
        if (UnlockedIds.Contains(Def.ContentId))
            continue;

        bool bMet = true;
        if (Profile->PlayerLevel < Def.RequiredLevel)
            bMet = false;
        if (Profile->TotalRaces < Def.RequiredRaces)
            bMet = false;
        if (Profile->TotalDistanceDriven < Def.RequiredDriftMeters)
            bMet = false;

        if (bMet)
        {
            UnlockedIds.Add(Def.ContentId);
            NewlyUnlocked.Add(Def.ContentId);

            // Mirror unlocks into the profile for redundancy.
            if (Def.ContentType == TEXT("part"))
                Profile->UnlockPart(Def.ContentId);
            else if (Def.ContentType == TEXT("material"))
                Profile->UnlockMaterial(Def.ContentId);
            else if (Def.ContentType == TEXT("decal"))
                Profile->UnlockDecal(Def.ContentId);

            UE_LOG(LogTemp, Log, TEXT("[raceGPS] Unlocked %s (%s)"), *Def.DisplayName, *Def.ContentId);
        }
    }

    if (NewlyUnlocked.Num() > 0)
    {
        SaveUnlockState();
    }

    return NewlyUnlocked;
}

FUnlockProgress UUnlockSystem::GetUnlockProgress(const FString& ContentId, UPlayerProfileSaveGame* Profile) const
{
    FUnlockProgress Progress;
    Progress.ContentId = ContentId;

    if (!Profile)
    {
        Progress.NextRequirementText = TEXT("No profile");
        return Progress;
    }

    if (UnlockedIds.Contains(ContentId))
    {
        Progress.bUnlocked = true;
        Progress.ProgressPercent = 1.0f;
        return Progress;
    }

    const FUnlockDefinition* Def = Definitions.FindByPredicate([&](const FUnlockDefinition& D)
    {
        return D.ContentId == ContentId;
    });

    if (!Def)
    {
        Progress.NextRequirementText = TEXT("Unknown content");
        return Progress;
    }

    float LevelPct   = Def->RequiredLevel > 0 ? FMath::Clamp(static_cast<float>(Profile->PlayerLevel) / Def->RequiredLevel, 0.0f, 1.0f) : 1.0f;
    float RacesPct   = Def->RequiredRaces > 0 ? FMath::Clamp(static_cast<float>(Profile->TotalRaces) / Def->RequiredRaces, 0.0f, 1.0f) : 1.0f;
    float DriftPct   = Def->RequiredDriftMeters > 0.0f ? FMath::Clamp(Profile->TotalDistanceDriven / Def->RequiredDriftMeters, 0.0f, 1.0f) : 1.0f;

    Progress.ProgressPercent = FMath::Min(LevelPct, FMath::Min(RacesPct, DriftPct));

    if (LevelPct < 1.0f)
    {
        Progress.NextRequirementText = FString::Printf(TEXT("Reach Level %d"), Def->RequiredLevel);
    }
    else if (RacesPct < 1.0f)
    {
        Progress.NextRequirementText = FString::Printf(TEXT("Complete %d Races"), Def->RequiredRaces);
    }
    else if (DriftPct < 1.0f)
    {
        Progress.NextRequirementText = FString::Printf(TEXT("Drift %.0fm"), Def->RequiredDriftMeters);
    }
    else
    {
        Progress.NextRequirementText = TEXT("Ready to unlock");
    }

    return Progress;
}

TArray<FUnlockDefinition> UUnlockSystem::GetAllDefinitions() const
{
    return Definitions;
}

void UUnlockSystem::ForceUnlock(const FString& ContentId)
{
    if (!UnlockedIds.Contains(ContentId))
    {
        UnlockedIds.Add(ContentId);
        SaveUnlockState();
    }
}

bool UUnlockSystem::SaveUnlockState()
{
    TSharedPtr<FJsonObject> Root = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Arr;
    for (const FString& Id : UnlockedIds)
    {
        Arr.Add(MakeShared<FJsonValueString>(Id));
    }
    Root->SetArrayField(TEXT("unlocked"), Arr);

    FString Content;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Content);
    FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);

    IFileManager::Get().MakeDirectory(*FPaths::GetPath(GetUnlockStatePath()), true);
    bool bSuccess = FFileHelper::SaveStringToFile(Content, *GetUnlockStatePath());
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Unlock state saved (%d items)"), UnlockedIds.Num());
    }
    return bSuccess;
}

bool UUnlockSystem::LoadUnlockState()
{
    FString Content;
    if (!FFileHelper::LoadFileToString(Content, *GetUnlockStatePath()))
        return false;

    TSharedPtr<FJsonObject> Root;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (!FJsonSerializer::Deserialize(Reader, Root))
        return false;

    const TArray<TSharedPtr<FJsonValue>>* Arr;
    if (Root->TryGetArrayField(TEXT("unlocked"), Arr))
    {
        UnlockedIds.Empty();
        for (const auto& Val : *Arr)
        {
            FString Id;
            if (Val->TryGetString(Id))
            {
                UnlockedIds.Add(Id);
            }
        }
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Unlock state loaded (%d items)"), UnlockedIds.Num());
    return true;
}

FString UUnlockSystem::GetUnlockStatePath() const
{
    return FPaths::ProjectSavedDir() / TEXT("unlock_state.json");
}

FString UUnlockSystem::GetUnlockDefinitionsPath() const
{
    return FPaths::ProjectSavedDir() / TEXT("unlock_definitions.json");
}
