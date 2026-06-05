#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RoadMeshGenerator.generated.h"

class UProceduralMeshComponent;

UCLASS()
class RACEGPSAKRONBETA_API ARoadMeshGenerator : public AActor
{
    GENERATED_BODY()

public:
    ARoadMeshGenerator(const FObjectInitializer& ObjectInitializer);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Roads")
    FString XodrPath = TEXT("citypacks/akron-oh-beta-001/akron.xodr");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Roads")
    float RoadHeightOffset = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Roads")
    bool bUseFlatShading = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Roads")
    int32 MaxRoadsPerFrame = 50;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Roads")
    void GenerateRoadMeshes();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Roads")
    void ClearRoadMeshes();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Roads")
    void GenerateRoadMeshAsync();

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Roads")
    int32 TotalRoadsGenerated = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Roads")
    bool bGenerationComplete = false;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY()
    TArray<TObjectPtr<UProceduralMeshComponent>> RoadMeshes;

    UPROPERTY()
    TArray<struct FAkronRoadSegment> PendingRoads;

    int32 PendingIndex = 0;
    bool bAsyncGenerating = false;

    void GenerateRoadMesh(const struct FAkronRoadSegment& Segment, UProceduralMeshComponent* Mesh);
    void ProcessBatch();
};
