#pragma once

#include <algorithm>
#include <cmath>

/** Portable result rules shared by the physical grid and regression tests. */
namespace RaceResultPolicy
{
    struct ProgressState
    {
        double PreviousS = 0.0;
        double PreviousTimeSec = 0.0;
        double SplineDistance = 0.0;
        double RaceProgress = 0.0;
        double FinishTimeSec = 0.0;
        int CompletedLaps = 0;
        bool bHaveSample = false;
        bool bFinished = false;
    };

    inline double Wrap(double S, double Length)
    {
        const double Wrapped = std::fmod(S, Length);
        return Wrapped < 0.0 ? Wrapped + Length : Wrapped;
    }

    // A recovery changes the sampling origin, never distance or completed laps.
    inline void Rebase(ProgressState& State, double S, double Length, double RaceTimeSec)
    {
        if (State.bFinished || !std::isfinite(S) || !std::isfinite(Length)
            || Length <= 0.0 || !std::isfinite(RaceTimeSec) || RaceTimeSec < 0.0)
        {
            return;
        }
        State.PreviousS = Wrap(S, Length);
        State.SplineDistance = State.PreviousS;
        State.PreviousTimeSec = RaceTimeSec;
        State.bHaveSample = true;
    }

    inline void Recover(ProgressState& State, double S, double Length, double RaceTimeSec)
    {
        if (State.bFinished || !std::isfinite(S) || !std::isfinite(Length)
            || Length <= 0.0 || !std::isfinite(RaceTimeSec) || RaceTimeSec < 0.0)
        {
            return;
        }
        if (State.bHaveSample)
        {
            double Ds = Wrap(S, Length) - State.PreviousS;
            if (Ds > 0.5 * Length) { Ds -= Length; }
            else if (Ds < -0.5 * Length) { Ds += Length; }
            // Re-driving after a backward recovery must not count the same road twice.
            State.RaceProgress += std::min(0.0, Ds);
        }
        Rebase(State, S, Length, RaceTimeSec);
    }

    // Both physical cars are sampled together against the session's racing clock.
    // Returns true only when a new lap is completed, at the actual start/finish wrap.
    inline bool Sample(ProgressState& State, double S, double Length, double RaceTimeSec,
        bool bRacing, int TargetLaps = 1)
    {
        if (!bRacing || State.bFinished || !std::isfinite(S) || !std::isfinite(Length)
            || Length <= 0.0 || !std::isfinite(RaceTimeSec) || RaceTimeSec < 0.0)
        {
            return false;
        }
        S = Wrap(S, Length);
        if (!State.bHaveSample)
        {
            // A car behind the grid line is behind the leader, not almost a lap ahead.
            State.RaceProgress = S > 0.85 * Length ? S - Length : S;
            Rebase(State, S, Length, RaceTimeSec);
            return false;
        }
        const double Dt = RaceTimeSec - State.PreviousTimeSec;
        if (Dt <= 0.0)
        {
            return false;
        }
        double Ds = S - State.PreviousS;
        if (Ds > 0.5 * Length) { Ds -= Length; }
        else if (Ds < -0.5 * Length) { Ds += Length; }

        // Reject projection jumps/teleports. Reverse movement subtracts progress.
        const double MaxDs = std::max(2000.0, 8000.0 * Dt);
        if (std::abs(Ds) > MaxDs)
        {
            // Keep the last valid sample: a transient projection on another segment
            // must neither add distance nor discard the distance actually driven.
            return false;
        }

        const bool bForwardWrap = Ds > 0.0 && State.PreviousS > 0.8 * Length && S < 0.2 * Length;
        const double CrossingTime = bForwardWrap
            ? State.PreviousTimeSec + Dt * (Length - State.PreviousS) / Ds
            : RaceTimeSec;
        State.RaceProgress += Ds;
        Rebase(State, S, Length, RaceTimeSec);
        const double NextLapDistance = (State.CompletedLaps + 1) * Length;
        if (!bForwardWrap || State.RaceProgress + 1e-6 < NextLapDistance)
        {
            return false;
        }

        ++State.CompletedLaps;
        if (State.CompletedLaps >= std::max(1, TargetLaps))
        {
            State.bFinished = true;
            State.FinishTimeSec = CrossingTime;
            State.RaceProgress = NextLapDistance;
            State.SplineDistance = 0.0;
        }
        return true;
    }

    template <typename Entry>
    inline bool IsAhead(const Entry& A, const Entry& B)
    {
        if (A.bFinished != B.bFinished) { return A.bFinished; }
        if (A.bFinished)
        {
            if (A.LastLapTimeSec != B.LastLapTimeSec) { return A.LastLapTimeSec < B.LastLapTimeSec; }
        }
        else if (A.RaceProgress != B.RaceProgress)
        {
            return A.RaceProgress > B.RaceProgress;
        }
        // Exact ties remain stable regardless of actor/controller tick order.
        return A.SlotIndex < B.SlotIndex;
    }
}
