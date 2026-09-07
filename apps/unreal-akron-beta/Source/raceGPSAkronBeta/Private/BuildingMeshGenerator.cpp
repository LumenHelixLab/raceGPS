#include "BuildingMeshGenerator.h"
#include "AkronXodrImporter.h"
#include "RaceGPSGeoFrame.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Engine/World.h"

ABuildingMeshGenerator::ABuildingMeshGenerator()
{
    PrimaryActorTick.bCanEverTick = true;

    ProceduralMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("BuildingMesh"));
    RootComponent = ProceduralMesh;
    ProceduralMesh->bUseAsyncCooking = true;
}

void ABuildingMeshGenerator::GenerateBuildingsAsync()
{
    LoadBuildingsJson();
    CurrentBuildingIndex = 0;
    GeneratedCount = 0;
    bGenerating = true;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Starting async building generation: %d buildings"), Buildings.Num());
}

void ABuildingMeshGenerator::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bGenerating && CurrentBuildingIndex < Buildings.Num())
    {
        int32 BatchSize = FMath::Min(BuildingsPerFrame, Buildings.Num() - CurrentBuildingIndex);
        GenerateBuildingBatch(BatchSize);
    }
    else if (bGenerating)
    {
        bGenerating = false;
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Building generation complete: %d buildings"), GeneratedCount);
    }
}

void ABuildingMeshGenerator::LoadBuildingsJson()
{
    Buildings.Empty();

    FString FullPath = FPaths::ProjectDir() / BuildingsJsonPath;
    FString Content;
    if (!FFileHelper::LoadFileToString(Content, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Failed to load buildings JSON: %s"), *FullPath);
        return;
    }

    TSharedPtr<FJsonObject> Root;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (!FJsonSerializer::Deserialize(Reader, Root))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Failed to parse buildings JSON"));
        return;
    }

    FString Frame, FootprintSpace;
    const TSharedPtr<FJsonObject>* Origin = nullptr;
    double FileLat = 0.0, FileLon = 0.0;
    if (!Root->TryGetStringField(TEXT("coordinate_frame"), Frame) ||
        Frame != UTF8_TO_TCHAR(RaceGPSGeoFrame::SourceFrame) ||
        !Root->TryGetStringField(TEXT("footprint_space"), FootprintSpace) ||
        (FootprintSpace != TEXT("wgs84-degrees") && FootprintSpace != TEXT("eqc-enu-m")) ||
        !Root->TryGetObjectField(TEXT("origin"), Origin) ||
        !(*Origin)->TryGetNumberField(TEXT("lat"), FileLat) || !(*Origin)->TryGetNumberField(TEXT("lon"), FileLon) ||
        !FMath::IsNearlyEqual(FileLat, OriginLat, 1.e-10) || !FMath::IsNearlyEqual(FileLon, OriginLon, 1.e-10))
    {
        UE_LOG(LogTemp, Error, TEXT("[raceGPS] Building coordinate frame/origin mismatch; regenerate the pack"));
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* Arr;
    if (!Root->TryGetArrayField(TEXT("buildings"), Arr))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] No 'buildings' array in JSON"));
        return;
    }

    for (const auto& Val : *Arr)
    {
        const TSharedPtr<FJsonObject>* Obj;
        if (!Val->TryGetObject(Obj))
            continue;

        FBuildingData B;
        (*Obj)->TryGetStringField(TEXT("id"), B.Id);
        if (!(*Obj)->TryGetStringField(TEXT("building_type"), B.Type))
            (*Obj)->TryGetStringField(TEXT("type"), B.Type);
        (*Obj)->TryGetStringField(TEXT("name"), B.Name);
        if (!(*Obj)->TryGetNumberField(TEXT("height_meters"), B.Height))
            (*Obj)->TryGetNumberField(TEXT("height"), B.Height);
        (*Obj)->TryGetNumberField(TEXT("area_m2"), B.AreaM2);

        const TArray<TSharedPtr<FJsonValue>>* FpArr;
        if ((*Obj)->TryGetArrayField(TEXT("footprint"), FpArr))
        {
            for (const auto& FpVal : *FpArr)
            {
                const TSharedPtr<FJsonObject>* FpObj;
                if (!FpVal->TryGetObject(FpObj))
                    continue;
                double A = 0.0, C = 0.0;
                const bool bGeographic = FootprintSpace == TEXT("wgs84-degrees");
                if (!(*FpObj)->TryGetNumberField(bGeographic ? TEXT("lat") : TEXT("x"), A) ||
                    !(*FpObj)->TryGetNumberField(bGeographic ? TEXT("lon") : TEXT("y"), C) ||
                    !FMath::IsFinite(A) || !FMath::IsFinite(C))
                {
                    UE_LOG(LogTemp, Error, TEXT("[raceGPS] Invalid building footprint"));
                    Buildings.Empty();
                    return;
                }
                if (bGeographic)
                {
                    const FVector P = UAkronXodrImporter::GeoToWorld(A, C, OriginLat, OriginLon);
                    B.Footprint.Add(FVector2D(P.X, P.Y));
                }
                else
                {
                    const auto P = RaceGPSGeoFrame::ToUnreal(A, C);
                    B.Footprint.Add(FVector2D(P.X, P.Y));
                }
            }
        }

        // OSM polygon rings repeat the first point; the mesh closes it itself.
        if (B.Footprint.Num() > 3 && B.Footprint[0].Equals(B.Footprint.Last(), 0.01))
            B.Footprint.Pop();
        if (B.Footprint.Num() < 3 || !FMath::IsFinite(B.Height) || B.Height <= 0.0f)
        {
            Buildings.Empty();
            return;
        }
        Buildings.Add(B);
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Loaded %d buildings from JSON"), Buildings.Num());
}

void ABuildingMeshGenerator::GenerateBuildingBatch(int32 Count)
{
    int32 EndIndex = FMath::Min(CurrentBuildingIndex + Count, Buildings.Num());

    for (int32 i = CurrentBuildingIndex; i < EndIndex; ++i)
    {
        CreateBuildingMesh(Buildings[i], i);
    }

    GeneratedCount += (EndIndex - CurrentBuildingIndex);
    CurrentBuildingIndex = EndIndex;
}

void ABuildingMeshGenerator::CreateBuildingMesh(const FBuildingData& Building, int32 SectionIndex)
{
    if (Building.Footprint.Num() < 3)
        return;

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FProcMeshTangent> Tangents;

    int32 N = Building.Footprint.Num();
    float H = Building.Height * 100.0f;

    // Wall vertices: bottom ring then top ring
    for (int32 i = 0; i < N; ++i)
    {
        FVector2D P = Building.Footprint[i];
        Vertices.Add(FVector(P.X, P.Y, 0.0f));
        UVs.Add(FVector2D(static_cast<float>(i) / N, 0.0f));
    }
    for (int32 i = 0; i < N; ++i)
    {
        FVector2D P = Building.Footprint[i];
        Vertices.Add(FVector(P.X, P.Y, H));
        UVs.Add(FVector2D(static_cast<float>(i) / N, 1.0f));
    }

    // Roof center vertex
    FVector2D Center(0.0f, 0.0f);
    for (const FVector2D& P : Building.Footprint)
    {
        Center += P;
    }
    Center /= static_cast<float>(N);
    int32 RoofCenterIdx = Vertices.Num();
    Vertices.Add(FVector(Center.X, Center.Y, H));
    UVs.Add(FVector2D(0.5f, 0.5f));

    // Wall triangles (quad per edge)
    for (int32 i = 0; i < N; ++i)
    {
        int32 i2 = (i + 1) % N;
        int32 b1 = i;
        int32 b2 = i2;
        int32 t1 = i + N;
        int32 t2 = i2 + N;

        // Two triangles per wall quad
        Triangles.Add(b1); Triangles.Add(t1); Triangles.Add(b2);
        Triangles.Add(b2); Triangles.Add(t1); Triangles.Add(t2);
    }

    // Roof triangles (fan from center)
    for (int32 i = 0; i < N; ++i)
    {
        int32 i2 = (i + 1) % N;
        Triangles.Add(RoofCenterIdx);
        Triangles.Add(i2 + N);
        Triangles.Add(i + N);
    }

    // Normals
    Normals.Init(FVector::UpVector, Vertices.Num());
    for (int32 i = 0; i < Vertices.Num(); ++i)
    {
        Tangents.Add(FProcMeshTangent(1.0f, 0.0f, 0.0f));
    }

    UMaterialInterface* Mat = GetMaterialForType(Building.Type);
    ProceduralMesh->CreateMeshSection(SectionIndex, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, true);
    if (Mat)
    {
        ProceduralMesh->SetMaterial(SectionIndex, Mat);
    }

    // Cull distance
    ProceduralMesh->SetMeshSectionVisible(SectionIndex, true);
}

UMaterialInterface* ABuildingMeshGenerator::GetMaterialForType(const FString& Type) const
{
    if (Type == TEXT("commercial") || Type == TEXT("office"))
        return MaterialGlass;
    if (Type == TEXT("industrial"))
        return MaterialIndustrial;
    if (Type == TEXT("residential_low") || Type == TEXT("residential_mid"))
        return MaterialResidential;
    if (Type == TEXT("religious") || Type == TEXT("education"))
        return MaterialBrick;
    return MaterialConcrete;
}
