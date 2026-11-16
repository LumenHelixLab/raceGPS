#pragma once

#include <algorithm>
#include <cmath>

// Engine-independent decisions used by the physical driver, not a second simulation.
namespace RaceAIBehaviorPolicy
{
struct Vector { double x, y, z; };
struct Box { Vector center, halfX, halfY, halfZ; };

inline double Dot(Vector a, Vector b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline double Radius(const Box& box, Vector axis)
{
    return std::abs(Dot(box.halfX, axis)) + std::abs(Dot(box.halfY, axis))
        + std::abs(Dot(box.halfZ, axis));
}

// Box half-axes are transformed directly from component space. Projecting a world
// AABB here instead would count yaw twice and block a safe parallel pass at 45deg.
inline double BumperGapMetres(const Box& own, const Box& other, Vector direction)
{
    const double length = std::hypot(direction.x, direction.y);
    if (length < 1e-8) return -1.0;
    const Vector forward{direction.x / length, direction.y / length, 0};
    const Vector right{-forward.y, forward.x, 0};
    const Vector delta{other.center.x - own.center.x, other.center.y - own.center.y,
        other.center.z - own.center.z};
    const double ahead = Dot(delta, forward);
    if (ahead < 0 || std::abs(delta.z) > Radius(own, {0, 0, 1}) + Radius(other, {0, 0, 1}))
        return -1.0;
    if (std::abs(Dot(delta, right)) > Radius(own, right) + Radius(other, right) + 50.0)
        return -1.0;
    return std::max(0.0, ahead - Radius(own, forward) - Radius(other, forward)) * 0.01;
}

struct DriveInput
{
    double throttle;
    double brake;
    double signedTorque;
    int targetGear; // zero means preserve the current automatic gear
};

// The same adapter is used with Chaos' bitfield settings and in portable tests.
// Capture once: repeated Tick input writes must not replace the human's settings.
struct OverrideSettings
{
    bool savedReverseAsBrake = false;
    bool savedThrottleAsBrake = false;
    bool active = false;

    template <typename Movement>
    void Apply(Movement& movement)
    {
        if (!active)
        {
            savedReverseAsBrake = movement.bReverseAsBrake;
            savedThrottleAsBrake = movement.bThrottleAsBrake;
            active = true;
        }
        movement.bReverseAsBrake = false;
        movement.bThrottleAsBrake = false;
    }

    template <typename Movement>
    void Restore(Movement& movement)
    {
        if (!active) return;
        movement.bReverseAsBrake = savedReverseAsBrake;
        movement.bThrottleAsBrake = savedThrottleAsBrake;
        active = false;
    }
};

// Chaos throttle is 0..1; reverse requires gear -1. Never change direction at speed.
inline DriveInput ResolveDriveInput(double signedThrottle, double brake, bool handbrake,
    double forwardSpeedKmh, int currentGear)
{
    if (!std::isfinite(signedThrottle) || !std::isfinite(brake) || !std::isfinite(forwardSpeedKmh))
        return {0, 1, 0, 0};
    signedThrottle = std::clamp(signedThrottle, -1.0, 1.0);
    brake = std::clamp(brake, 0.0, 1.0);
    if (handbrake || brake >= 0.15 || std::abs(signedThrottle) < 1e-4)
        return {0, brake, 0, 0};
    const int direction = signedThrottle < 0 ? -1 : 1;
    if (forwardSpeedKmh * direction < -2.0)
        return {0, std::max(brake, 0.6), 0, 0};
    const int gear = (direction < 0 && currentGear >= 0) ? -1
        : ((direction > 0 && currentGear <= 0) ? 1 : 0);
    return {std::abs(signedThrottle), brake, signedThrottle, gear};
}

inline bool ShouldResetAfterAttempt(double upDot, double absCteCm, double maxCteCm,
    double distanceMovedCm)
{
    return upDot < 0.35 || absCteCm > maxCteCm || distanceMovedCm < 100.0;
}

// Keep the recovery anchor, or use a station the car has physically reversed to.
// Wrapping at start/finish must not turn a small backward move into forward gain.
inline double RecoveryStation(double anchorS, double currentS, double trackLength)
{
    if (trackLength <= 0) return 0;
    double delta = std::fmod(currentS - anchorS, trackLength);
    if (delta > trackLength * 0.5) delta -= trackLength;
    if (delta < -trackLength * 0.5) delta += trackLength;
    return delta > 0 ? anchorS : currentS;
}
}
