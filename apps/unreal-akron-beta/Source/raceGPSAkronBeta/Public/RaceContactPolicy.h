#pragma once

#include <algorithm>
#include <cmath>

// Feedback only: Chaos owns collision impulses. Inputs are km/h, seconds and metres.
// Shared by player/AI; no extra shove, damage advantage or hidden catch-up force.
namespace RaceContactPolicy
{
inline bool PresentsPair(bool selfPlayer, bool otherPlayer, unsigned selfId, unsigned otherId)
{
    if (selfPlayer != otherPlayer) return selfPlayer;
    return selfId < otherId;
}

enum class Kind { None, Scrape, Tap, Impact };
struct Feedback { Kind kind = Kind::None; double strength = 0; double impactKmh = 0; };

inline Feedback Evaluate(double normalKmh, double tangentKmh, double impulseDeltaKmh)
{
    if (!std::isfinite(normalKmh) || !std::isfinite(tangentKmh) || !std::isfinite(impulseDeltaKmh))
        return {};
    const double impact = std::max(std::abs(normalKmh), std::abs(impulseDeltaKmh));
    const double slide = std::abs(tangentKmh);
    if (impact >= 20) return {Kind::Impact, std::clamp(impact / 60, 0.0, 1.0), impact};
    if (impact >= 5) return {Kind::Tap, std::clamp(impact / 60, 0.0, 1.0), impact};
    if (slide >= 5) return {Kind::Scrape, std::clamp(slide / 80, 0.0, 1.0), impact};
    return {};
}

inline bool ShouldEmit(double now, double previous)
{
    return std::isfinite(now) && std::isfinite(previous) && now - previous >= 0.15;
}

struct Commands { double throttle; double brake; double targetKmh; };
inline Commands Drive(double requestedKmh, double speedKmh, double gapMetres, double leaderKmh)
{
    if (!std::isfinite(requestedKmh) || !std::isfinite(speedKmh) ||
        !std::isfinite(gapMetres) || !std::isfinite(leaderKmh)) return {0, 1, 0};
    double target = std::max(0.0, requestedKmh);
    if (gapMetres >= 0)
    {
        // Two metres stand-off, then a 1.2 second following gap.
        const double available = std::max(0.0, gapMetres - 2.0);
        const double safe = available * 3.6 / 1.2;
        const double closingAllowance = std::max(0.0, leaderKmh) + available;
        target = std::min(target, std::min(safe, closingAllowance));
    }
    const double error = target - std::max(0.0, speedKmh);
    return {std::clamp(error / 20.0, 0.0, 1.0), std::clamp(-error / 20.0, 0.0, 1.0), target};
}
}
