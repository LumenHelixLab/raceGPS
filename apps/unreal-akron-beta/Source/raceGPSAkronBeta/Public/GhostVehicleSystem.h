// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "GhostVehicleSystem.generated.h"

USTRUCT()
struct FGhostFrame
{
    GENERATED_BODY()

    UPROPERTY()
    float Timestamp = 0.0f;

    UPROPERTY()
    FVector Location = FVector::ZeroVector;

    UPROPERTY()
    FRotator Rotation = FRotator::ZeroRotator;

    UPROPERTY()
    FVector Velocity = FVector::ZeroVector;
};

/**
 * Records player lap data and replays a ghost vehicle on subsequent runs.
 */
UCLASS()
class RACEGPSAKRONBETA_API UGhostVehicleSystem : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    void StartRecording();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    void StopRecording();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    void SaveGhost(const FString& TrackId);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    bool LoadGhost(const FString& TrackId);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    class AGhostVehicle* SpawnGhostActor(UWorld* World, const FVector& SpawnLocation = FVector::ZeroVector);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Ghost")
    void RecordFrame(float DeltaTime, const FVector& Location, const FRotator& Rotation, const FVector& Velocity);

    UFUNCTION(BlueprintPure, Category = "raceGPS|Ghost")
    bool IsRecording() const { return bRecording; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|Ghost")
    int32 GetFrameCount() const { return Frames.Num(); }

    UFUNCTION(BlueprintPure, Category = "raceGPS|Ghost")
    float GetRecordingDuration() const { return RecordingDuration; }

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Ghost")
    float RecordInterval = 0.05f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Ghost")
    TSubclassOf<class AGhostVehicle> GhostVehicleClass;

protected:
    UPROPERTY()
    TArray<FGhostFrame> Frames;

private:
    bool bRecording = false;
    float RecordingDuration = 0.0f;
    float LastRecordTime = 0.0f;

    FString GetGhostPath(const FString& TrackId) const;
};
