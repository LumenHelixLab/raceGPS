#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "CourseCreatorWidget.generated.h"

UCLASS()
class RACEGPSAKRONBETA_API UCourseCreatorWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void StartRecording();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void PlaceCheckpoint();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void StopRecording();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void SaveRoute();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void DiscardRoute();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|CourseCreator")
    void TickRecording(float DeltaTime);

    UFUNCTION(BlueprintPure, Category = "raceGPS|CourseCreator")
    bool IsRecording() const { return bRecording; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|CourseCreator")
    int32 GetWaypointCount() const { return RecordedWaypoints.Num(); }

    UFUNCTION(BlueprintPure, Category = "raceGPS|CourseCreator")
    int32 GetCheckpointCount() const { return RecordedCheckpoints.Num(); }

    UFUNCTION(BlueprintPure, Category = "raceGPS|CourseCreator")
    float GetRecordedDistance() const { return RecordedDistance; }

    UPROPERTY(meta = (BindWidget))
    class UButton* StartRecordButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* PlaceCheckpointButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* StopRecordButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* SaveRouteButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* DiscardButton;

    UPROPERTY(meta = (BindWidget))
    class UEditableTextBox* RouteNameInput;

    UPROPERTY(meta = (BindWidget))
    class UEditableTextBox* RouteDescriptionInput;

    UPROPERTY(meta = (BindWidget))
    class UComboBoxString* DifficultySelector;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* StatusText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* StatsText;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|CourseCreator")
    float WaypointInterval = 10.0f; // Record waypoint every 10 meters

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|CourseCreator")
    float MinRouteLength = 500.0f; // Minimum route length in meters

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|CourseCreator")
    int32 MinCheckpoints = 3;

protected:
    UFUNCTION()
    void UpdateStatsDisplay();

    UFUNCTION()
    FString GenerateRouteId() const;

    bool bRecording = false;
    float RecordedDistance = 0.0f;
    float DistanceSinceLastWaypoint = 0.0f;
    FVector LastWaypointLocation;

    UPROPERTY()
    TArray<FVector> RecordedWaypoints;

    UPROPERTY()
    TArray<FVector> RecordedCheckpoints;
};
