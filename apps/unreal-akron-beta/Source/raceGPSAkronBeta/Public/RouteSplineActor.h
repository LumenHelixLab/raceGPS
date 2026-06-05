#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RouteSplineActor.generated.h"

class USplineComponent;
class USplineMeshComponent;

UCLASS()
class RACEGPSAKRONBETA_API ARouteSplineActor : public AActor
{
    GENERATED_BODY()

public:
    ARouteSplineActor(const FObjectInitializer& ObjectInitializer);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    FString RouteId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    FLinearColor RouteColor = FLinearColor(0.0f, 0.8f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    float RibbonWidth = 200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    float RibbonThickness = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    float SplinePointSpacing = 500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    bool bGenerateRibbonMesh = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Route")
    bool bShowCheckpointArrows = true;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    void BuildSplineFromWaypoints(const TArray<FVector>& Waypoints);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    void ClearRoute();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    FVector GetClosestPointOnSpline(const FVector& WorldLocation) const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    float GetDistanceAlongSpline(const FVector& WorldLocation) const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    FVector GetLocationAtDistance(float Distance) const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Route")
    FRotator GetRotationAtDistance(float Distance) const;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "raceGPS|Route")
    TObjectPtr<USplineComponent> Spline;

protected:
    virtual void BeginPlay() override;

    UPROPERTY()
    TArray<TObjectPtr<USplineMeshComponent>> RibbonSegments;

    UPROPERTY()
    TArray<TObjectPtr<UStaticMeshComponent>> CheckpointArrows;

    void GenerateRibbonMesh();
    void GenerateCheckpointArrows(const TArray<FVector>& Waypoints);
    void UpdateSplineTangents();
};
