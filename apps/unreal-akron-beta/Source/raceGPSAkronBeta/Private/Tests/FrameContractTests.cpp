#include "Misc/AutomationTest.h"
#include "AkronXodrImporter.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSFrameA_100mEast, "raceGPS.Frame.A.GeoToWorld.100mEast",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSFrameA_100mEast::RunTest(const FString& Parameters)
{
    const double OriginLat = 41.51722;
    const double OriginLon = -81.68306;
    const double MetersPerLon = static_cast<double>(UAkronXodrImporter::MetersPerDegreeLatConst) * FMath::Cos(FMath::DegreesToRadians(OriginLat));
    const double DLon = 100.0 / MetersPerLon;
    const FVector A = UAkronXodrImporter::GeoToWorld(OriginLat, OriginLon, OriginLat, OriginLon);
    const FVector B = UAkronXodrImporter::GeoToWorld(OriginLat, OriginLon + DLon, OriginLat, OriginLon);
    const double Dist = FVector::Dist(A, B);
    TestTrue(TEXT("100m east within 1cm"), FMath::Abs(Dist - 10000.0) <= 1.0);
    TestTrue(TEXT("northing near 0"), FMath::Abs(B.Y - A.Y) <= 1.0);
    TestTrue(TEXT("easting positive"), B.X > A.X);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSFrameA_100mNorth, "raceGPS.Frame.A.GeoToWorld.100mNorth",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSFrameA_100mNorth::RunTest(const FString& Parameters)
{
    const double OriginLat = 41.51722;
    const double OriginLon = -81.68306;
    const double DLat = 100.0 / static_cast<double>(UAkronXodrImporter::MetersPerDegreeLatConst);
    const FVector A = UAkronXodrImporter::GeoToWorld(OriginLat, OriginLon, OriginLat, OriginLon);
    const FVector B = UAkronXodrImporter::GeoToWorld(OriginLat + DLat, OriginLon, OriginLat, OriginLon);
    const double Dist = FVector::Dist(A, B);
    TestTrue(TEXT("100m north within 1cm"), FMath::Abs(Dist - 10000.0) <= 1.0);
    TestTrue(TEXT("easting near 0"), FMath::Abs(B.X - A.X) <= 1.0);
    TestTrue(TEXT("northing positive"), B.Y > A.Y);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSFrameA_RoadWidth7m, "raceGPS.Frame.A.RoadWidth.7m",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSFrameA_RoadWidth7m::RunTest(const FString& Parameters)
{
    const float Half = 7.0f * UAkronXodrImporter::MetersToUU * 0.5f;
    TestTrue(TEXT("half-width 350cm +/-1"), FMath::Abs(Half - 350.0f) <= 1.0f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSFrameA_CompassYaw, "raceGPS.Frame.A.CompassToUeYaw",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSFrameA_CompassYaw::RunTest(const FString& Parameters)
{
    auto Near = [](float A, float B) {
        return FMath::Abs(FMath::FindDeltaAngleDegrees(A, B)) <= 0.1f;
    };
    TestTrue(TEXT("north"), Near(UAkronXodrImporter::CompassHeadingDegToUeYaw(0.0f), 90.0f));
    TestTrue(TEXT("east"), Near(UAkronXodrImporter::CompassHeadingDegToUeYaw(90.0f), 0.0f));
    TestTrue(TEXT("south"), Near(UAkronXodrImporter::CompassHeadingDegToUeYaw(180.0f), -90.0f));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FraceGPSFrameA_PackedGeoSign, "raceGPS.Frame.A.PackedGeoSign",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FraceGPSFrameA_PackedGeoSign::RunTest(const FString& Parameters)
{
    const float Lat = 41.5f;
    const float Lon = -81.7f;
    const FVector Packed(Lon, 0.0f, -Lat);
    float OutLat = 0.0f, OutLon = 0.0f;
    UAkronXodrImporter::UnpackPackedGeoDegrees(Packed, OutLat, OutLon);
    TestEqual(TEXT("lat"), OutLat, Lat);
    TestEqual(TEXT("lon"), OutLon, Lon);
    const FVector W1 = UAkronXodrImporter::GeoToWorld(Lat, Lon, Lat, Lon);
    const FVector W2 = UAkronXodrImporter::GeoToWorldFromPacked(Packed, Lat, Lon);
    TestTrue(TEXT("packed matches geo"), W1.Equals(W2, 0.01f));
    return true;
}
