// Copyright raceGPS. All Rights Reserved.

#include "GhostVehicleSystem.h"
#include "GhostVehicle.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

void UGhostVehicleSystem::StartRecording()
{
    bRecording = true;
    RecordingDuration = 0.0f;
    LastRecordTime = 0.0f;
    Frames.Empty();
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Ghost recording started"));
}

void UGhostVehicleSystem::StopRecording()
{
    bRecording = false;
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Ghost recording stopped. Frames: %d, Duration: %.2fs"),
        Frames.Num(), RecordingDuration);
}

void UGhostVehicleSystem::RecordFrame(float DeltaTime, const FVector& Location, const FRotator& Rotation, const FVector& Velocity)
{
    if (!bRecording)
        return;

    RecordingDuration += DeltaTime;

    if (Frames.Num() == 0 || RecordingDuration - LastRecordTime >= RecordInterval)
    {
        FGhostFrame Frame;
        Frame.Timestamp = RecordingDuration;
        Frame.Location = Location;
        Frame.Rotation = Rotation;
        Frame.Velocity = Velocity;
        Frames.Add(Frame);
        LastRecordTime = RecordingDuration;
    }
}

void UGhostVehicleSystem::SaveGhost(const FString& TrackId)
{
    TSharedPtr<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("track_id"), TrackId);
    Root->SetNumberField(TEXT("version"), 1);
    Root->SetNumberField(TEXT("duration"), RecordingDuration);
    Root->SetNumberField(TEXT("frame_count"), Frames.Num());
    Root->SetNumberField(TEXT("record_interval"), RecordInterval);

    TArray<TSharedPtr<FJsonValue>> FrameArray;
    for (const FGhostFrame& Frame : Frames)
    {
        TSharedPtr<FJsonObject> FrameObj = MakeShared<FJsonObject>();
        FrameObj->SetNumberField(TEXT("t"), Frame.Timestamp);
        FrameObj->SetNumberField(TEXT("x"), Frame.Location.X);
        FrameObj->SetNumberField(TEXT("y"), Frame.Location.Y);
        FrameObj->SetNumberField(TEXT("z"), Frame.Location.Z);
        FrameObj->SetNumberField(TEXT("pitch"), Frame.Rotation.Pitch);
        FrameObj->SetNumberField(TEXT("yaw"), Frame.Rotation.Yaw);
        FrameObj->SetNumberField(TEXT("roll"), Frame.Rotation.Roll);
        FrameObj->SetNumberField(TEXT("vx"), Frame.Velocity.X);
        FrameObj->SetNumberField(TEXT("vy"), Frame.Velocity.Y);
        FrameObj->SetNumberField(TEXT("vz"), Frame.Velocity.Z);
        FrameArray.Add(MakeShared<FJsonValueObject>(FrameObj));
    }
    Root->SetArrayField(TEXT("frames"), FrameArray);

    FString Content;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Content);
    FJsonSerializer::Serialize(Root.ToSharedRef(), Writer);

    FString FullPath = GetGhostPath(TrackId);
    FPaths::MakeStandardFilename(FullPath);
    IFileManager::Get().MakeDirectory(*FPaths::GetPath(FullPath), true);

    bool bSuccess = FFileHelper::SaveStringToFile(Content, *FullPath);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Ghost saved: %s (%d frames)"), *FullPath, Frames.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("[raceGPS] Failed to save ghost: %s"), *FullPath);
    }
}

bool UGhostVehicleSystem::LoadGhost(const FString& TrackId)
{
    FString FullPath = GetGhostPath(TrackId);
    FPaths::MakeStandardFilename(FullPath);

    FString Content;
    if (!FFileHelper::LoadFileToString(Content, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Ghost file not found: %s"), *FullPath);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Content);
    if (!FJsonSerializer::Deserialize(Reader, Root))
    {
        UE_LOG(LogTemp, Error, TEXT("[raceGPS] Failed to parse ghost JSON"));
        return false;
    }

    Frames.Empty();
    RecordingDuration = 0.0f;

    const TArray<TSharedPtr<FJsonValue>>* FrameArray;
    if (Root->TryGetArrayField(TEXT("frames"), FrameArray))
    {
        Frames.Reserve(FrameArray->Num());
        for (const TSharedPtr<FJsonValue>& Val : *FrameArray)
        {
            const TSharedPtr<FJsonObject>* FrameObj;
            if (!Val->TryGetObject(FrameObj))
                continue;

            FGhostFrame Frame;
            (*FrameObj)->TryGetNumberField(TEXT("t"), Frame.Timestamp);
            double X = 0.0, Y = 0.0, Z = 0.0;
            (*FrameObj)->TryGetNumberField(TEXT("x"), X);
            (*FrameObj)->TryGetNumberField(TEXT("y"), Y);
            (*FrameObj)->TryGetNumberField(TEXT("z"), Z);
            Frame.Location = FVector(static_cast<float>(X), static_cast<float>(Y), static_cast<float>(Z));

            double Pitch = 0.0, Yaw = 0.0, Roll = 0.0;
            (*FrameObj)->TryGetNumberField(TEXT("pitch"), Pitch);
            (*FrameObj)->TryGetNumberField(TEXT("yaw"), Yaw);
            (*FrameObj)->TryGetNumberField(TEXT("roll"), Roll);
            Frame.Rotation = FRotator(static_cast<float>(Pitch), static_cast<float>(Yaw), static_cast<float>(Roll));

            double VX = 0.0, VY = 0.0, VZ = 0.0;
            (*FrameObj)->TryGetNumberField(TEXT("vx"), VX);
            (*FrameObj)->TryGetNumberField(TEXT("vy"), VY);
            (*FrameObj)->TryGetNumberField(TEXT("vz"), VZ);
            Frame.Velocity = FVector(static_cast<float>(VX), static_cast<float>(VY), static_cast<float>(VZ));

            Frames.Add(Frame);
            RecordingDuration = FMath::Max(RecordingDuration, Frame.Timestamp);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Ghost loaded: %s (%d frames, %.2fs)"),
        *FullPath, Frames.Num(), RecordingDuration);
    return Frames.Num() > 0;
}

AGhostVehicle* UGhostVehicleSystem::SpawnGhostActor(UWorld* World, const FVector& SpawnLocation)
{
    if (!World)
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] Cannot spawn ghost: invalid world"));
        return nullptr;
    }

    if (!GhostVehicleClass)
    {
        UE_LOG(LogTemp, Warning, TEXT("[raceGPS] GhostVehicleClass not set"));
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AGhostVehicle* Ghost = World->SpawnActor<AGhostVehicle>(GhostVehicleClass, SpawnLocation, FRotator::ZeroRotator, Params);
    if (Ghost)
    {
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Ghost actor spawned at %s"), *SpawnLocation.ToString());
    }
    return Ghost;
}

FString UGhostVehicleSystem::GetGhostPath(const FString& TrackId) const
{
    return FPaths::ProjectSavedDir() / TEXT("Ghosts") /
        FString::Printf(TEXT("ghost_%s.json"), *TrackId);
}
