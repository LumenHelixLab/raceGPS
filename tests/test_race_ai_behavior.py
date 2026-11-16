"""Run the production rival clearance, reverse and recovery decisions as C++."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public"


@pytest.fixture(scope="module")
def rival_policy(tmp_path_factory):
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        pytest.skip("Native C++ compiler unavailable")
    assert (PUBLIC / "RaceAIBehaviorPolicy.h").exists(), "Production rival behavior policy is missing"
    directory = tmp_path_factory.mktemp("rival_policy")
    source = directory / "rival.cpp"
    source.write_text(r'''
#include "RaceAIBehaviorPolicy.h"
#include "RaceContactPolicy.h"
#include <cassert>
#include <cmath>
#include <string>
using namespace RaceAIBehaviorPolicy;

static Box car(double x, double y, double z, double yaw) {
    const double c = std::cos(yaw), s = std::sin(yaw);
    return {{x, y, z}, {250*c, 250*s, 0}, {-100*s, 100*c, 0}, {0, 0, 75}};
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string name = argv[1];
    if (name == "parallel_pass") {
        // Five-metre cars, two metres wide, with one metre between their sides.
        // A yaw change must not turn this clear pass into a braking obstacle.
        for (double yaw : {0.0, 0.7853981633974483, 1.5707963267948966}) {
            const double c = std::cos(yaw), s = std::sin(yaw);
            const auto own = car(0, 0, 0, yaw);
            const auto other = car(200*c - 300*s, 200*s + 300*c, 0, yaw);
            const double gap = BumperGapMetres(own, other, {c, s, 0});
            assert(gap < 0);
            const auto drive = RaceContactPolicy::Drive(80, 40, gap, 40);
            assert(drive.throttle > 0 && drive.brake == 0);
        }
    } else if (name == "forward_clearance") {
        const double c = std::sqrt(0.5);
        const auto own = car(0, 0, 0, 0.7853981633974483);
        const double gap = BumperGapMetres(own, car(1000*c, 1000*c, 0, 0.7853981633974483), {c, c, 0});
        assert(std::abs(gap - 5.0) < 1e-8);
        assert(RaceContactPolicy::Drive(80, 40, gap, 0).brake > 0);
        // The long side of a crossing car really does occupy the lane.
        assert(std::abs(BumperGapMetres(car(0, 0, 0, 0), car(600, 200, 0, 1.5707963267948966), {1, 0, 0}) - 2.5) < 1e-8);
        assert(BumperGapMetres(car(0, 0, 0, 0), car(600, 0, 1000, 0), {1, 0, 0}) < 0);
    } else if (name == "rear_clearance") {
        const auto own = car(0, 0, 0, 0);
        const auto rear = car(-700, 0, 0, 0);
        assert(BumperGapMetres(own, rear, {1, 0, 0}) < 0);
        assert(std::abs(BumperGapMetres(own, rear, {-1, 0, 0}) - 2.0) < 1e-8);
        assert(BumperGapMetres(own, car(700, 0, 0, 0), {-1, 0, 0}) < 0);
        const auto stop = RaceContactPolicy::Drive(8, 4, BumperGapMetres(own, rear, {-1, 0, 0}), 0);
        assert(stop.throttle == 0 && stop.brake > 0);
    } else if (name == "reverse_gear") {
        const auto reverse = ResolveDriveInput(-0.25, 0, false, 0, 1);
        assert(reverse.targetGear == -1 && reverse.throttle == 0.25);
        assert(reverse.brake == 0 && reverse.signedTorque == -0.25);
        const auto reversing = ResolveDriveInput(-0.25, 0, false, -3, -1);
        assert(reversing.targetGear == 0 && reversing.throttle == 0.25 && reversing.signedTorque < 0);
        const auto forward = ResolveDriveInput(0.7, 0, false, 60, 3);
        assert(forward.targetGear == 0 && forward.throttle == 0.7 && forward.signedTorque > 0);
    } else if (name == "brake_before_direction_change") {
        const auto forward = ResolveDriveInput(-0.25, 0, false, 20, 2);
        assert(forward.throttle == 0 && forward.signedTorque == 0 && forward.brake >= 0.6 && forward.targetGear == 0);
        const auto reverse = ResolveDriveInput(0.7, 0, false, -12, -1);
        assert(reverse.throttle == 0 && reverse.brake >= 0.6 && reverse.targetGear == 0);
        const auto hold = ResolveDriveInput(-0.25, 1, true, 0, 1);
        assert(hold.throttle == 0 && hold.signedTorque == 0 && hold.brake == 1);
    } else if (name == "override_settings_restore") {
        struct MovementSettings { unsigned bReverseAsBrake : 1; unsigned bThrottleAsBrake : 1; } mode{true, true};
        OverrideSettings saved;
        saved.Apply(mode);
        assert(!mode.bReverseAsBrake && !mode.bThrottleAsBrake);
        saved.Apply(mode); // Tick writes must not overwrite the original snapshot.
        saved.Restore(mode);
        assert(mode.bReverseAsBrake && mode.bThrottleAsBrake);
        mode = {false, true};
        saved.Restore(mode); // An extra clear must not restore stale settings.
        assert(!mode.bReverseAsBrake && mode.bThrottleAsBrake);
        saved.Apply(mode);
        saved.Restore(mode);
        assert(!mode.bReverseAsBrake && mode.bThrottleAsBrake);
    } else if (name == "torque_clears_after_accelerating") {
        assert(ResolveDriveInput(0.7, 0, false, 20, 2).signedTorque > 0);
        assert(ResolveDriveInput(0.7, 1, false, 20, 2).signedTorque == 0);
        assert(ResolveDriveInput(0, 0, false, 20, 2).signedTorque == 0);
        assert(ResolveDriveInput(0.7, 0, true, 20, 2).signedTorque == 0);
    } else if (name == "stalled_recovery") {
        // An overturned car or a failed manoeuvre can require reset right on the line.
        assert(ShouldResetAfterAttempt(-1, 0, 1800, 150));
        assert(ShouldResetAfterAttempt(1, 20, 1800, 0));
        assert(!ShouldResetAfterAttempt(1, 20, 1800, 150));
        assert(ShouldResetAfterAttempt(1, 2000, 1800, 150));
    } else if (name == "recovery_never_advances") {
        assert(RecoveryStation(1000, 1200, 10000) == 1000);
        assert(RecoveryStation(1000, 900, 10000) == 900);
        assert(RecoveryStation(9900, 50, 10000) == 9900);
        assert(RecoveryStation(50, 9900, 10000) == 9900);
        // A grid car 6.5 metres behind the start stays there during recovery.
        assert(RecoveryStation(9350, 9350, 10000) == 9350);
    } else {
        assert(false && "Unknown behavior case");
    }
}
''')
    binary = directory / "rival"
    subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                    "-I", str(PUBLIC), str(source), "-o", str(binary)], check=True)
    return binary


@pytest.mark.parametrize("case", [
    "parallel_pass", "forward_clearance", "rear_clearance", "reverse_gear",
    "brake_before_direction_change", "stalled_recovery", "recovery_never_advances",
    "override_settings_restore", "torque_clears_after_accelerating",
])
def test_rival_behavior(rival_policy, case):
    subprocess.run([str(rival_policy), case], check=True)
