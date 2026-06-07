// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrafficAISpawner.generated.h"

class USplineComponent;
class ATrafficVehicle;

/**
 * Spawns traffic vehicles on roads with configurable density.
 * Vehicles follow spline paths at speed limits.
 */
UCLASS()
class RACEGPSAKRONBETA_API ATrafficAISpawner : public AActor
{
    GENERATED_BODY()

public:
    ATrafficAISpawner(const FObjectInitializer& ObjectInitializer);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    int32 MaxTrafficDensity = 20;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    float SpeedLimitKmh = 45.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    float SpawnRadius = 2000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    float DespawnRadius = 3000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    float SpawnInterval = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    TSubclassOf<ATrafficVehicle> TrafficVehicleClass;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|TrafficAI")
    TArray<TObjectPtr<USplineComponent>> RoadSplines;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|TrafficAI")
    void SpawnTraffic(int32 Density);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|TrafficAI")
    void DespawnFarTraffic(const FVector& PlayerLocation, float MaxDistance);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|TrafficAI")
    void UpdateTraffic(float DeltaTime);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|TrafficAI")
    void ClearAllTraffic();

    UFUNCTION(BlueprintPure, Category = "raceGPS|TrafficAI")
    int32 GetActiveTrafficCount() const { return ActiveTraffic.Num(); }

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY()
    TArray<TObjectPtr<ATrafficVehicle>> ActiveTraffic;

    float SpawnTimer = 0.0f;

    void TrySpawnVehicle();
    void AssignSplineToVehicle(ATrafficVehicle* Vehicle);
    TArray<FVector> SampleSplinePoints(USplineComponent* Spline) const;
    float GetSpeedForSpline(USplineComponent* Spline) const;
};
