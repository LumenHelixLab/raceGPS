#include "RaceResultPolicy.h"
#include <cassert>
#include <cmath>
#include <string>

struct Standing
{
    int SlotIndex;
    bool bFinished;
    double LastLapTimeSec;
    double RaceProgress;
};

// One kilometre fixture, sampled at a physical 10 m/s with an exact finish at 100 s.
static void DriveToFinishApproach(RaceResultPolicy::ProgressState& state)
{
    RaceResultPolicy::Sample(state, 0.0, 100000.0, 0.0, true);
    for (int step = 1; step <= 99; ++step)
    {
        assert(!RaceResultPolicy::Sample(state, step * 1000.0, 100000.0, step, true));
    }
}

int main(int argc, char** argv)
{
    assert(argc == 2);
    const std::string scenario(argv[1]);
    if (scenario == "finished_order")
    {
        const Standing winner{1, true, 80.0, 327582.0};
        const Standing later{0, true, 81.0, 329582.0};
        assert(RaceResultPolicy::IsAhead(winner, later));
        assert(!RaceResultPolicy::IsAhead(later, winner));
        const Standing unfinished{0, false, 0.0, 400000.0};
        assert(RaceResultPolicy::IsAhead(winner, unfinished));
    }
    else if (scenario == "unfinished_order")
    {
        const Standing ahead{1, false, 0.0, 240000.0};
        const Standing behind{0, false, 0.0, 239000.0};
        assert(RaceResultPolicy::IsAhead(ahead, behind));
        assert(!RaceResultPolicy::IsAhead(behind, ahead));
    }
    else if (scenario == "ties")
    {
        const Standing first{0, true, 80.0, 330000.0};
        const Standing second{1, true, 80.0, 340000.0};
        assert(RaceResultPolicy::IsAhead(first, second));
        assert(!RaceResultPolicy::IsAhead(second, first));
        assert(!RaceResultPolicy::IsAhead(first, first));
    }
    else if (scenario == "actual_finish_line")
    {
        RaceResultPolicy::ProgressState state;
        DriveToFinishApproach(state);
        assert(!RaceResultPolicy::Sample(state, 99600.0, 100000.0, 99.6, true));
        assert(!state.bFinished);
        assert(RaceResultPolicy::Sample(state, 0.0, 100000.0, 100.0, true));
        assert(state.CompletedLaps == 1);
        assert(std::abs(state.FinishTimeSec - 100.0) < 1e-8);
    }
    else if (scenario == "common_clock")
    {
        RaceResultPolicy::ProgressState player;
        RaceResultPolicy::ProgressState rival;
        // Different world/possession ages cannot enter the race clock.
        RaceResultPolicy::Sample(player, 0.0, 100000.0, 500.0, false);
        RaceResultPolicy::Sample(rival, 0.0, 100000.0, 1000.0, false);
        DriveToFinishApproach(player);
        DriveToFinishApproach(rival);
        assert(RaceResultPolicy::Sample(player, 1000.0, 100000.0, 101.0, true));
        assert(RaceResultPolicy::Sample(rival, 500.0, 100000.0, 101.0, true));
        assert(std::abs(player.FinishTimeSec - 100.0) < 1e-8);
        assert(std::abs(rival.FinishTimeSec - 100.33333333333333) < 1e-8);
    }
    else if (scenario == "same_tick_finish")
    {
        RaceResultPolicy::ProgressState player;
        RaceResultPolicy::ProgressState rival;
        DriveToFinishApproach(player);
        DriveToFinishApproach(rival);
        // Rival is processed second but crossed first within the same sample interval.
        RaceResultPolicy::Sample(player, 500.0, 100000.0, 101.0, true);
        RaceResultPolicy::Sample(rival, 1000.0, 100000.0, 101.0, true);
        const Standing playerResult{0, player.bFinished, player.FinishTimeSec, player.RaceProgress};
        const Standing rivalResult{1, rival.bFinished, rival.FinishTimeSec, rival.RaceProgress};
        assert(RaceResultPolicy::IsAhead(rivalResult, playerResult));
    }
    else if (scenario == "countdown_and_spawn")
    {
        RaceResultPolicy::ProgressState state;
        for (int step = 0; step <= 101; ++step)
        {
            RaceResultPolicy::Sample(state, std::fmod(step * 1000.0, 100000.0), 100000.0, step, false);
        }
        assert(state.CompletedLaps == 0);
        assert(!state.bFinished);
        RaceResultPolicy::Sample(state, 99350.0, 100000.0, 0.0, true);
        assert(state.RaceProgress == -650.0);
        assert(!RaceResultPolicy::Sample(state, 350.0, 100000.0, 1.0, true));
        assert(state.CompletedLaps == 0);
        assert(state.RaceProgress == 350.0);
    }
    else if (scenario == "reverse_and_jump")
    {
        RaceResultPolicy::ProgressState state;
        RaceResultPolicy::Sample(state, 0.0, 100000.0, 0.0, true);
        RaceResultPolicy::Sample(state, 99000.0, 100000.0, 1.0, true);
        assert(state.RaceProgress == -1000.0);
        assert(!RaceResultPolicy::Sample(state, 1000.0, 100000.0, 2.0, true));
        assert(state.CompletedLaps == 0);
        assert(!RaceResultPolicy::Sample(state, 90000.0, 100000.0, 2.01, true));
        assert(state.RaceProgress <= 1000.0);
        assert(!RaceResultPolicy::Sample(state, 100.0, 100000.0, 2.02, true));
        assert(!state.bFinished);
    }
    else if (scenario == "immutable_finish")
    {
        RaceResultPolicy::ProgressState state;
        DriveToFinishApproach(state);
        RaceResultPolicy::Sample(state, 0.0, 100000.0, 100.0, true);
        assert(!RaceResultPolicy::Sample(state, 5000.0, 100000.0, 105.0, true));
        assert(!RaceResultPolicy::Sample(state, 95000.0, 100000.0, 195.0, false));
        assert(state.CompletedLaps == 1);
        assert(state.FinishTimeSec == 100.0);
        assert(state.RaceProgress == 100000.0);
    }
    else if (scenario == "recovery")
    {
        RaceResultPolicy::ProgressState state;
        DriveToFinishApproach(state);
        // Even a misplaced recovery across the line cannot claim a lap or a position gain.
        RaceResultPolicy::Rebase(state, 100.0, 100000.0, 99.5);
        assert(state.RaceProgress == 99000.0);
        assert(!state.bFinished);
        assert(!RaceResultPolicy::Sample(state, 200.0, 100000.0, 99.6, true));
        assert(state.CompletedLaps == 0);
        assert(state.RaceProgress == 99100.0);
    }
    else if (scenario == "backward_recovery")
    {
        RaceResultPolicy::ProgressState state;
        DriveToFinishApproach(state);
        for (int repeat = 0; repeat < 3; ++repeat)
        {
            RaceResultPolicy::Recover(state, 98000.0, 100000.0, 99.5 + repeat * 2.0);
            assert(state.RaceProgress == 98000.0);
            assert(!RaceResultPolicy::Sample(state, 99000.0, 100000.0, 100.5 + repeat * 2.0, true));
            assert(state.RaceProgress == 99000.0);
            assert(state.CompletedLaps == 0);
        }
    }
    else if (scenario == "projection_noise")
    {
        RaceResultPolicy::ProgressState state;
        RaceResultPolicy::Sample(state, 0.0, 100000.0, 0.0, true);
        for (int step = 1; step <= 99; ++step)
        {
            RaceResultPolicy::Sample(state, step * 1000.0, 100000.0, step, true);
            if (step == 50)
            {
                assert(!RaceResultPolicy::Sample(state, 90000.0, 100000.0, 50.01, true));
                assert(state.RaceProgress == 50000.0);
            }
        }
        assert(RaceResultPolicy::Sample(state, 0.0, 100000.0, 100.0, true));
        assert(state.FinishTimeSec == 100.0);
    }
    else if (scenario == "rematches")
    {
        RaceResultPolicy::ProgressState state;
        for (int race = 0; race < 3; ++race)
        {
            state = {};
            assert(!state.bFinished && state.CompletedLaps == 0 && state.FinishTimeSec == 0.0);
            DriveToFinishApproach(state);
            assert(RaceResultPolicy::Sample(state, 0.0, 100000.0, 100.0, true));
            assert(state.FinishTimeSec == 100.0);
        }
    }
    else if (scenario == "multiple_laps")
    {
        RaceResultPolicy::ProgressState state;
        RaceResultPolicy::Sample(state, 0.0, 100000.0, 0.0, true, 2);
        for (int step = 1; step <= 200; ++step)
        {
            RaceResultPolicy::Sample(state, std::fmod(step * 1000.0, 100000.0), 100000.0, step, true, 2);
            if (step == 100)
            {
                assert(state.CompletedLaps == 1);
                assert(!state.bFinished && state.FinishTimeSec == 0.0);
            }
        }
        assert(state.CompletedLaps == 2 && state.bFinished);
        assert(state.FinishTimeSec == 200.0);
    }
    else
    {
        assert(false && "Unknown scenario");
    }
}
