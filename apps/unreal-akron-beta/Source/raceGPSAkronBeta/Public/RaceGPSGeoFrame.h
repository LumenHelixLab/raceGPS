#pragma once
#include <cmath>

// Engine-independent math, compiled directly by the portable conformance test.
// Keep in agreement with tools/geo_frame.py and the versioned frame contract.
namespace RaceGPSGeoFrame
{
    inline constexpr const char* SourceFrame = "racegps-eqc-enu-m-v1";
    inline constexpr const char* WorldFrame = "racegps-ue-esu-cm-v1";
    inline constexpr double MetersPerDegree = 111320.0;
    inline constexpr double CentimetersPerMeter = 100.0;
    inline constexpr double Pi = 3.14159265358979323846;
    struct Point { double X; double Y; double Z; };
    inline Point ToUnreal(double East, double North, double Up = 0.0)
    {
        return {East * CentimetersPerMeter, -North * CentimetersPerMeter, Up * CentimetersPerMeter};
    }
    inline Point FromGeographic(double Lat, double Lon, double OriginLat, double OriginLon)
    {
        return ToUnreal((Lon - OriginLon) * MetersPerDegree * std::cos(OriginLat * Pi / 180.0),
                        (Lat - OriginLat) * MetersPerDegree);
    }
    inline double CompassToYaw(double Heading)
    {
        double Yaw = std::fmod(Heading + 90.0, 360.0);
        if (Yaw < 0.0) Yaw += 360.0;
        return Yaw - 180.0;
    }
    inline Point LineEnd(double X, double Y, double HeadingRadians, double LengthMeters)
    {
        return ToUnreal(X + std::cos(HeadingRadians) * LengthMeters,
                        Y + std::sin(HeadingRadians) * LengthMeters);
    }
}
