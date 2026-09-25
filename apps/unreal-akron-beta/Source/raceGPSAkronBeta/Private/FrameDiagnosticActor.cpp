#include "FrameDiagnosticActor.h"
#include "AkronXodrImporter.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"

AFrameDiagnosticActor::AFrameDiagnosticActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AFrameDiagnosticActor::BeginPlay()
{
    Super::BeginPlay();
    if (bAutoDrawOnBeginPlay)
    {
        DrawDiagnostic();
    }
}

void AFrameDiagnosticActor::DrawDiagnostic()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    const FVector Origin = GetActorLocation();
    const float LenUU = LineLengthMeters * UAkronXodrImporter::MetersToUU;
    const float HalfW = RoadWidthMeters * UAkronXodrImporter::MetersToUU * 0.5f;

    const FVector East = Origin + FVector(LenUU, 0.0f, 0.0f);
    const FVector North = Origin + FVector(0.0f, LenUU, 0.0f);
    const FVector Up = Origin + FVector(0.0f, 0.0f, LenUU);

    DrawDebugLine(World, Origin, East, FColor::Red, true, -1.0f, 0, 8.0f);
    DrawDebugLine(World, Origin, North, FColor::Green, true, -1.0f, 0, 8.0f);
    DrawDebugLine(World, Origin, Up, FColor::Blue, true, -1.0f, 0, 8.0f);

    // 7 m-wide road strip centered on +X for 100 m
    const FVector RoadEnd = East;
    DrawDebugLine(World, Origin + FVector(0, HalfW, 2), RoadEnd + FVector(0, HalfW, 2), FColor::Yellow, true, -1.0f, 0, 4.0f);
    DrawDebugLine(World, Origin + FVector(0, -HalfW, 2), RoadEnd + FVector(0, -HalfW, 2), FColor::Yellow, true, -1.0f, 0, 4.0f);

    float EastLen = 0, NorthLen = 0, UpLen = 0, RoadW = 0;
    const bool Ok = SelfCheck(EastLen, NorthLen, UpLen, RoadW);
    UE_LOG(LogTemp, Log,
        TEXT("[raceGPS][FrameDiag] SOURCE_TO_UNREAL_FRAME_v1 self-check %s | east=%.2fcm north=%.2fcm up=%.2fcm roadWidth=%.2fcm (expect 10000/10000/10000/700 +/-1)"),
        Ok ? TEXT("PASS") : TEXT("FAIL"), EastLen, NorthLen, UpLen, RoadW);

    // Geo cross-check: 100 m east via GeoToWorld should match LenUU within 1 cm
    // Double math for the longitude delta: float32 rounds lon ~-81.7 to ~7.6e-6 deg (~30 cm).
    const double MetersPerLon = static_cast<double>(UAkronXodrImporter::MetersPerDegreeLatConst) * FMath::Cos(FMath::DegreesToRadians(static_cast<double>(OriginLat)));
    const double DLon = static_cast<double>(LineLengthMeters) / MetersPerLon;
    const FVector Geo0 = UAkronXodrImporter::GeoToWorld(OriginLat, OriginLon, OriginLat, OriginLon);
    const FVector GeoE = UAkronXodrImporter::GeoToWorld(OriginLat, static_cast<double>(OriginLon) + DLon, OriginLat, OriginLon);
    const double GeoEast = FVector::Dist(Geo0, GeoE);
    UE_LOG(LogTemp, Log, TEXT("[raceGPS][FrameDiag] GeoToWorld 100m-east length=%.3f cm (tol 1cm)"), GeoEast);
}

bool AFrameDiagnosticActor::SelfCheck(float& OutEastLenCm, float& OutNorthLenCm, float& OutUpLenCm, float& OutRoadWidthCm) const
{
    OutEastLenCm = LineLengthMeters * UAkronXodrImporter::MetersToUU;
    OutNorthLenCm = LineLengthMeters * UAkronXodrImporter::MetersToUU;
    OutUpLenCm = LineLengthMeters * UAkronXodrImporter::MetersToUU;
    OutRoadWidthCm = RoadWidthMeters * UAkronXodrImporter::MetersToUU;
    const float Tol = 1.0f;
    return FMath::Abs(OutEastLenCm - 10000.0f) <= Tol
        && FMath::Abs(OutNorthLenCm - 10000.0f) <= Tol
        && FMath::Abs(OutUpLenCm - 10000.0f) <= Tol
        && FMath::Abs(OutRoadWidthCm - 700.0f) <= Tol;
}
