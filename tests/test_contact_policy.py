"""Execute the production C++ contact/pace policy without requiring Unreal."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_contact_and_following_behavior(tmp_path):
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        pytest.skip("Native C++ compiler unavailable; run on portable Linux CI")
    header = ROOT / "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public/RaceContactPolicy.h"
    assert header.exists(), "Production contact policy is not implemented"
    source = tmp_path / "contact.cpp"
    source.write_text(r'''
#include "RaceContactPolicy.h"
#include <cassert>
#include <cmath>
#include <limits>
using namespace RaceContactPolicy;
int main() {
    // Exactly one sound/spark owner, including standalone AI locally controlled too.
    assert(PresentsPair(true, false, 9, 1));
    assert(!PresentsPair(false, true, 1, 9));
    assert(PresentsPair(false, false, 1, 9));
    assert(!PresentsPair(false, false, 9, 1));
    // No relative motion/impulse: no fake hit, regardless of world speed.
    assert(Evaluate(0, 0, 0).kind == Kind::None);
    assert(Evaluate(0, 30, 0).kind == Kind::Scrape);
    assert(Evaluate(8, 0, 0).kind == Kind::Tap);
    assert(Evaluate(30, 0, 0).kind == Kind::Impact);
    // Post-solver relative speed may be zero; impulse still records a hard hit.
    assert(Evaluate(0, 0, 25).kind == Kind::Impact);
    assert(Evaluate(-8, -30, -2).kind == Evaluate(8, 30, 2).kind);
    assert(Evaluate(10000, 0, 0).strength == 1.0);
    assert(Evaluate(std::numeric_limits<double>::quiet_NaN(), 0, 0).kind == Kind::None);
    assert(!ShouldEmit(1.0, 0.95));
    assert(ShouldEmit(1.2, 0.95));
    assert(!ShouldEmit(0.9, 1.0));
    // Clear road retains the corner-speed target; never pins throttle blindly.
    auto fast = Drive(40, 60, -1, 0);
    assert(fast.throttle == 0 && fast.brake > 0);
    auto slow = Drive(60, 20, -1, 0);
    assert(slow.throttle > 0 && slow.brake == 0);
    // Gap is bumper clearance, metres; standstill or closing into a rival brakes.
    auto blocked = Drive(80, 30, 1, 0);
    assert(blocked.throttle == 0 && blocked.brake > 0);
    auto follow = Drive(80, 50, 10, 20);
    assert(follow.targetKmh < 50 && follow.brake > 0);
    auto clear = Drive(80, 50, 100, 20);
    assert(clear.targetKmh == 80 && clear.throttle > 0);
    assert(Drive(80, 50, 0, 50).targetKmh == 0);
}
''')
    binary = tmp_path / "contact"
    subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                    "-I", str(header.parent), str(source), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
