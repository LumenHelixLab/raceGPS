#include "StreetFurnitureSpawner.h"
#include "AkronXodrImporter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Engine/World.h"
#include "Components/StaticMeshComponent.h"

AStreetFurnitureSpawner::AStreetFurnitureSpawner()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AStreetFurnitureSpawner::SpawnFurnitureAsync()
{
    LoadIntersections();
    CurrentIndex = 0;
    bSpawning = true;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Starting async furniture spawn: %d placements"), Placements.Num());
}

void AStreetFurnitureSpawner::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bSpawning && CurrentIndex < Placements.Num())
    {
        int32 BatchSize = FMath::Min(FurniturePerFrame, Placements.Num() - CurrentIndex);
        SpawnBatch(BatchSize);
    }
    else if (bSpawning)
    {
        bSpawning = false;
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Furniture spawn complete: %d items"), Placements.Num());
    }
}

void AStreetFurnitureSpawner::LoadIntersections()
{
    Placements.Empty();

    FString FullPath = FPaths::ProjectDir() / RoadGraphJsonPath;
    FString Content;
    if (!FFileHelper::LoadFileToString(Content, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Failed to load road graph JSON: %s"), *FullPath);
        return;
    }

    TSharedPtr<FJsonObject> Root;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (!FJsonSerializer::Deserialize(Reader, Root))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Failed to parse road graph JSON"));
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* IntersectionsArr;
    if (!Root->TryGetArrayField(TEXT("intersections"), IntersectionsArr))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] No 'intersections' array in road graph"));
        return;
    }

    // Load pack origin; convert via SOURCE_TO_UNREAL_FRAME_v1 GeoToWorld (cm).
    FVector SpawnCenter = FVector::ZeroVector;
    float OriginLat = 41.08f;
    float OriginLon = -81.52f;
    FString ManifestPath;
    // Prefer active city layout when available; fall back to Akron beta path.
    FRaceGPSCityLayout Layout;
    if (UAkronXodrImporter::ResolveCityLayout(Layout) && !Layout.ManifestPath.IsEmpty())
    {
        ManifestPath = FPaths::ProjectDir() / Layout.ManifestPath;
    }
    else
    {
        ManifestPath = FPaths::ProjectDir() / TEXT("citypacks/akron-oh-beta-001/akron_semantic_manifest.json");
    }
    FString ManifestContent;
    if (FFileHelper::LoadFileToString(ManifestContent, *ManifestPath))
    {
        TSharedPtr<FJsonObject> ManifestRoot;
        TSharedRef<TJsonReader<>> ManifestReader = TJsonReaderFactory<>::Create(ManifestContent);
        if (FJsonSerializer::Deserialize(ManifestReader, ManifestRoot))
        {
            const TSharedPtr<FJsonObject>* OriginObj;
            if (ManifestRoot->TryGetObjectField(TEXT("origin"), OriginObj))
            {
                double Lat = 0.0, Lon = 0.0;
                (*OriginObj)->TryGetNumberField(TEXT("lat"), Lat);
                (*OriginObj)->TryGetNumberField(TEXT("lon"), Lon);
                OriginLat = static_cast<float>(Lat);
                OriginLon = static_cast<float>(Lon);
            }
        }
    }
    SpawnCenter = UAkronXodrImporter::GeoToWorld(OriginLat, OriginLon, OriginLat, OriginLon);

    for (const auto& Val : *IntersectionsArr)
    {
        const TSharedPtr<FJsonObject>* Obj;
        if (!Val->TryGetObject(Obj))
            continue;

        double Lat = 0.0, Lon = 0.0;
        (*Obj)->TryGetNumberField(TEXT("lat"), Lat);
        (*Obj)->TryGetNumberField(TEXT("lon"), Lon);

        FVector WorldLoc = UAkronXodrImporter::GeoToWorld(
            static_cast<float>(Lat), static_cast<float>(Lon), OriginLat, OriginLon);

        // SpawnRadius is meters (property); compare in cm world.
        const float SpawnRadiusUU = SpawnRadius * UAkronXodrImporter::MetersToUU;
        if (FVector::Dist2D(WorldLoc, SpawnCenter) > SpawnRadiusUU)
            continue;

        FFurniturePlacement PL;
        PL.Location = WorldLoc;
        PL.Rotation = FRotator::ZeroRotator;
        PL.Type = TEXT("traffic_light");
        Placements.Add(PL);

        // Offset meters -> cm
        FVector Offset = FVector(
            FMath::RandRange(-5.0f, 5.0f) * UAkronXodrImporter::MetersToUU,
            FMath::RandRange(-5.0f, 5.0f) * UAkronXodrImporter::MetersToUU,
            0.0f);
        PL.Location = WorldLoc + Offset;
        PL.Type = TEXT("barrier");
        Placements.Add(PL);
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Loaded %d furniture placements"), Placements.Num());
}

void AStreetFurnitureSpawner::SpawnBatch(int32 Count)
{
    int32 EndIndex = FMath::Min(CurrentIndex + Count, Placements.Num());

    for (int32 i = CurrentIndex; i < EndIndex; ++i)
    {
        const FFurniturePlacement& P = Placements[i];
        if (P.Type == TEXT("traffic_light"))
        {
            SpawnTrafficLight(P.Location, P.Rotation);
        }
        else if (P.Type == TEXT("barrier"))
        {
            SpawnBarrier(P.Location, P.Rotation);
        }
    }

    CurrentIndex = EndIndex;
}

void AStreetFurnitureSpawner::SpawnTrafficLight(const FVector& Location, const FRotator& Rotation)
{
    // Placeholder: creates a simple actor representation
    // In production, this would spawn a CARLA traffic light mesh
    UE_LOG(LogTemp, Verbose, TEXT("[raceGPS] Spawn traffic light at %s"), *Location.ToString());
}

void AStreetFurnitureSpawner::SpawnBarrier(const FVector& Location, const FRotator& Rotation)
{
    UE_LOG(LogTemp, Verbose, TEXT("[raceGPS] Spawn barrier at %s"), *Location.ToString());
}

void AStreetFurnitureSpawner::SpawnBench(const FVector& Location, const FRotator& Rotation)
{
    UE_LOG(LogTemp, Verbose, TEXT("[raceGPS] Spawn bench at %s"), *Location.ToString());
}
