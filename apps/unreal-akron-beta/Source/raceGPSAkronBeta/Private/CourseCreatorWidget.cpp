#include "CourseCreatorWidget.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/EditableTextBox.h"
#include "Components/ComboBoxString.h"
#include "Kismet/GameplayStatics.h"
#include "ChaosVehiclePawn.h"
#include "ContributionCaptureComponent.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

void UCourseCreatorWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (StartRecordButton)
    {
        StartRecordButton->OnClicked.AddDynamic(this, &UCourseCreatorWidget::StartRecording);
    }
    if (PlaceCheckpointButton)
    {
        PlaceCheckpointButton->OnClicked.AddDynamic(this, &UCourseCreatorWidget::PlaceCheckpoint);
    }
    if (StopRecordButton)
    {
        StopRecordButton->OnClicked.AddDynamic(this, &UCourseCreatorWidget::StopRecording);
    }
    if (SaveRouteButton)
    {
        SaveRouteButton->OnClicked.AddDynamic(this, &UCourseCreatorWidget::SaveRoute);
    }
    if (DiscardButton)
    {
        DiscardButton->OnClicked.AddDynamic(this, &UCourseCreatorWidget::DiscardRoute);
    }

    if (DifficultySelector)
    {
        DifficultySelector->ClearOptions();
        DifficultySelector->AddOption(TEXT("easy"));
        DifficultySelector->AddOption(TEXT("medium"));
        DifficultySelector->AddOption(TEXT("hard"));
        DifficultySelector->AddOption(TEXT("extreme"));
        DifficultySelector->SetSelectedOption(TEXT("medium"));
    }

    UpdateStatsDisplay();
}

void UCourseCreatorWidget::StartRecording()
{
    AChaosVehiclePawn* Vehicle = Cast<AChaosVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (!Vehicle)
        return;

    bRecording = true;
    RecordedDistance = 0.0f;
    DistanceSinceLastWaypoint = 0.0f;
    RecordedWaypoints.Empty();
    RecordedCheckpoints.Empty();
    LastWaypointLocation = Vehicle->GetActorLocation();
    RecordedWaypoints.Add(LastWaypointLocation);

    if (StatusText)
    {
        StatusText->SetText(FText::FromString(TEXT("Recording... Drive the route!")));
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Course recording started"));
}

void UCourseCreatorWidget::PlaceCheckpoint()
{
    if (!bRecording)
        return;

    AChaosVehiclePawn* Vehicle = Cast<AChaosVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (!Vehicle)
        return;

    RecordedCheckpoints.Add(Vehicle->GetActorLocation());
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Checkpoint %d placed"), RecordedCheckpoints.Num());
    UpdateStatsDisplay();
}

void UCourseCreatorWidget::StopRecording()
{
    if (!bRecording)
        return;

    bRecording = false;

    // Add final waypoint
    AChaosVehiclePawn* Vehicle = Cast<AChaosVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (Vehicle)
    {
        RecordedWaypoints.Add(Vehicle->GetActorLocation());
    }

    if (StatusText)
    {
        if (RecordedDistance >= MinRouteLength && RecordedCheckpoints.Num() >= MinCheckpoints)
        {
            StatusText->SetText(FText::FromString(TEXT("Recording complete! Save your route.")));
        }
        else
        {
            StatusText->SetText(FText::FromString(FString::Printf(
                TEXT("Route too short! Need %.0fm and %d checkpoints."),
                MinRouteLength, MinCheckpoints)));
        }
    }

    UpdateStatsDisplay();
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Course recording stopped. Waypoints: %d, Checkpoints: %d, Distance: %.0fm"),
        RecordedWaypoints.Num(), RecordedCheckpoints.Num(), RecordedDistance);
}

void UCourseCreatorWidget::TickRecording(float DeltaTime)
{
    if (!bRecording)
        return;

    AChaosVehiclePawn* Vehicle = Cast<AChaosVehiclePawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
    if (!Vehicle)
        return;

    FVector CurrentLoc = Vehicle->GetActorLocation();
    float DeltaDist = FVector::Dist2D(CurrentLoc, LastWaypointLocation);
    RecordedDistance += DeltaDist;
    DistanceSinceLastWaypoint += DeltaDist;

    if (DistanceSinceLastWaypoint >= WaypointInterval)
    {
        RecordedWaypoints.Add(CurrentLoc);
        DistanceSinceLastWaypoint = 0.0f;
    }

    LastWaypointLocation = CurrentLoc;
    UpdateStatsDisplay();
}

void UCourseCreatorWidget::SaveRoute()
{
    if (RecordedDistance < MinRouteLength)
    {
        if (StatusText)
        {
            StatusText->SetText(FText::FromString(TEXT("Route too short! Drive more.")));
        }
        return;
    }

    if (RecordedCheckpoints.Num() < MinCheckpoints)
    {
        if (StatusText)
        {
            StatusText->SetText(FText::FromString(TEXT("Not enough checkpoints!")));
        }
        return;
    }

    FString RouteName = RouteNameInput ? RouteNameInput->GetText().ToString() : TEXT("Unnamed Route");
    if (RouteName.IsEmpty())
        RouteName = TEXT("Unnamed Route");

    FString RouteDesc = RouteDescriptionInput ? RouteDescriptionInput->GetText().ToString() : TEXT("");
    FString Difficulty = DifficultySelector ? DifficultySelector->GetSelectedOption() : TEXT("medium");
    FString RouteId = GenerateRouteId();

    // Save to local JSON (user_routes folder)
    FString UserRoutesDir = FPaths::ProjectSavedDir() / TEXT("user_routes");
    IFileManager::Get().MakeDirectory(*UserRoutesDir, true);

    TSharedPtr<FJsonObject> RouteObj = MakeShared<FJsonObject>();
    RouteObj->SetStringField(TEXT("route_id"), RouteId);
    RouteObj->SetStringField(TEXT("route_name"), RouteName);
    RouteObj->SetStringField(TEXT("route_description"), RouteDesc);
    RouteObj->SetStringField(TEXT("difficulty"), Difficulty);
    RouteObj->SetNumberField(TEXT("distance_meters"), RecordedDistance);
    RouteObj->SetStringField(TEXT("created_at"), FDateTime::Now().ToString(TEXT("%Y-%m-%d")));

    // Waypoints
    TArray<TSharedPtr<FJsonValue>> WpArr;
    for (const FVector& Wp : RecordedWaypoints)
    {
        TSharedPtr<FJsonObject> Pt = MakeShared<FJsonObject>();
        Pt->SetNumberField(TEXT("x"), Wp.X);
        Pt->SetNumberField(TEXT("y"), Wp.Y);
        Pt->SetNumberField(TEXT("z"), Wp.Z);
        WpArr.Add(MakeShared<FJsonValueObject>(Pt));
    }
    RouteObj->SetArrayField(TEXT("waypoints"), WpArr);

    // Checkpoints
    TArray<TSharedPtr<FJsonValue>> CpArr;
    for (const FVector& Cp : RecordedCheckpoints)
    {
        TSharedPtr<FJsonObject> Pt = MakeShared<FJsonObject>();
        Pt->SetNumberField(TEXT("x"), Cp.X);
        Pt->SetNumberField(TEXT("y"), Cp.Y);
        Pt->SetNumberField(TEXT("z"), Cp.Z);
        CpArr.Add(MakeShared<FJsonValueObject>(Pt));
    }
    RouteObj->SetArrayField(TEXT("checkpoints"), CpArr);

    FString Content;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Content);
    FJsonSerializer::Serialize(RouteObj.ToSharedRef(), Writer);

    FString FilePath = UserRoutesDir / FString::Printf(TEXT("%s.json"), *RouteId);
    FFileHelper::SaveStringToFile(Content, *FilePath);

    // Submit to contribution system
    APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
    if (PC)
    {
        UContributionCaptureComponent* Capture = PC->FindComponentByClass<UContributionCaptureComponent>();
        if (Capture)
        {
            Capture->SubmitRouteCreation(RouteId, RouteName, RecordedWaypoints, RecordedCheckpoints, RecordedDistance, Difficulty);
        }
    }

    if (StatusText)
    {
        StatusText->SetText(FText::FromString(FString::Printf(TEXT("Route saved! ID: %s"), *RouteId)));
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Route saved: %s at %s"), *RouteId, *FilePath);
}

void UCourseCreatorWidget::DiscardRoute()
{
    bRecording = false;
    RecordedWaypoints.Empty();
    RecordedCheckpoints.Empty();
    RecordedDistance = 0.0f;

    if (RouteNameInput)
        RouteNameInput->SetText(FText::GetEmpty());
    if (RouteDescriptionInput)
        RouteDescriptionInput->SetText(FText::GetEmpty());
    if (StatusText)
        StatusText->SetText(FText::FromString(TEXT("Route discarded. Start over?")));

    UpdateStatsDisplay();
}

void UCourseCreatorWidget::UpdateStatsDisplay()
{
    if (!StatsText)
        return;

    FString Stats = FString::Printf(
        TEXT("Waypoints: %d | Checkpoints: %d | Distance: %.0fm"),
        RecordedWaypoints.Num(), RecordedCheckpoints.Num(), RecordedDistance
    );
    StatsText->SetText(FText::FromString(Stats));
}

FString UCourseCreatorWidget::GenerateRouteId() const
{
    return FString::Printf(TEXT("user_%s_%s"),
        *FDateTime::Now().ToString(TEXT("%Y%m%d")),
        *FGuid::NewGuid().ToString().Left(8));
}
