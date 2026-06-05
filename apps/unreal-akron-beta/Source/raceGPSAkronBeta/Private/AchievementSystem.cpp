#include "AchievementSystem.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

void UAchievementSystem::InitializeAchievements()
{
    auto Add = [this](const FString& Id, const FString& Title, const FString& Desc, int32 Target)
    {
        FAchievement A;
        A.Id = Id;
        A.Title = Title;
        A.Description = Desc;
        A.ProgressTarget = Target;
        Achievements.Add(Id, A);
    };

    Add(TEXT("first_race"), TEXT("First Steps"), TEXT("Complete your first race"), 1);
    Add(TEXT("gold_medalist"), TEXT("Gold Rush"), TEXT("Earn 3 gold medals"), 3);
    Add(TEXT("clean_driver"), TEXT("Clean Driver"), TEXT("Finish a race with zero collisions"), 1);
    Add(TEXT("speed_demon"), TEXT("Speed Demon"), TEXT("Reach 200 km/h"), 1);
    Add(TEXT("checkpoint_master"), TEXT("Checkpoint Master"), TEXT("Hit every checkpoint in a race"), 1);
    Add(TEXT("explorer"), TEXT("Explorer"), TEXT("Drive 50km total"), 1);
    Add(TEXT("night_racer"), TEXT("Night Racer"), TEXT("Complete a race at night"), 1);
    Add(TEXT("traffic_dodger"), TEXT("Traffic Dodger"), TEXT("Avoid 100 traffic vehicles"), 100);
    Add(TEXT("replay_watcher"), TEXT("Ghost Buster"), TEXT("Beat your own ghost"), 1);
    Add(TEXT("cartographer"), TEXT("Cartographer"), TEXT("Compile a new city"), 1);

    LoadAchievements();
}

void UAchievementSystem::UnlockAchievement(const FString& AchievementId)
{
    FAchievement* A = Achievements.Find(AchievementId);
    if (!A || A->bUnlocked)
        return;

    A->bUnlocked = true;
    A->UnlockDate = FDateTime::Now().ToString(TEXT("%Y-%m-%d"));
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Achievement unlocked: %s"), *A->Title);

    SaveAchievements();
}

void UAchievementSystem::AddProgress(const FString& AchievementId, int32 Amount)
{
    FAchievement* A = Achievements.Find(AchievementId);
    if (!A || A->bUnlocked)
        return;

    A->CurrentProgress += Amount;
    if (A->CurrentProgress >= A->ProgressTarget)
    {
        UnlockAchievement(AchievementId);
    }
    else
    {
        SaveAchievements();
    }
}

bool UAchievementSystem::IsUnlocked(const FString& AchievementId) const
{
    const FAchievement* A = Achievements.Find(AchievementId);
    return A && A->bUnlocked;
}

TArray<FAchievement> UAchievementSystem::GetAllAchievements() const
{
    TArray<FAchievement> Result;
    Achievements.GenerateValueArray(Result);
    return Result;
}

bool UAchievementSystem::SaveAchievements()
{
    TSharedPtr<FJsonObject> Root = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Arr;

    for (const auto& Pair : Achievements)
    {
        TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
        Obj->SetStringField(TEXT("id"), Pair.Value.Id);
        Obj->SetNumberField(TEXT("progress"), Pair.Value.CurrentProgress);
        Obj->SetBoolField(TEXT("unlocked"), Pair.Value.bUnlocked);
        Obj->SetStringField(TEXT("date"), Pair.Value.UnlockDate);
        Arr.Add(MakeShared<FJsonValueObject>(Obj));
    }
    Root->SetArrayField(TEXT("achievements"), Arr);

    FString Content;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Content);
    FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);

    return FFileHelper::SaveStringToFile(Content, *GetAchievementsPath());
}

bool UAchievementSystem::LoadAchievements()
{
    FString Content;
    if (!FFileHelper::LoadFileToString(Content, *GetAchievementsPath()))
        return false;

    TSharedPtr<FJsonObject> Root;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (!FJsonSerializer::Deserialize(Reader, Root))
        return false;

    const TArray<TSharedPtr<FJsonValue>>* Arr;
    if (!Root->TryGetArrayField(TEXT("achievements"), Arr))
        return false;

    for (const auto& Val : *Arr)
    {
        const TSharedPtr<FJsonObject>* Obj;
        if (!Val->TryGetObject(Obj))
            continue;

        FString Id;
        (*Obj)->TryGetStringField(TEXT("id"), Id);
        FAchievement* A = Achievements.Find(Id);
        if (!A)
            continue;

        (*Obj)->TryGetNumberField(TEXT("progress"), A->CurrentProgress);
        (*Obj)->TryGetBoolField(TEXT("unlocked"), A->bUnlocked);
        (*Obj)->TryGetStringField(TEXT("date"), A->UnlockDate);
    }

    return true;
}

FString UAchievementSystem::GetAchievementsPath() const
{
    return FPaths::ProjectSavedDir() / TEXT("achievements.json");
}
