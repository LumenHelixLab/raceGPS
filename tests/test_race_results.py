"""Execute the race grid's production result policy without an Unreal install."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public"


@pytest.fixture(scope="module")
def result_policy_binary(tmp_path_factory):
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        pytest.skip("Native C++ compiler unavailable")
    binary = tmp_path_factory.mktemp("race_results") / "race_results"
    subprocess.run(
        [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I", str(PUBLIC),
         str(ROOT / "tests/cpp/race_result_policy_test.cpp"), "-o", str(binary)],
        check=True,
    )
    return binary


@pytest.mark.parametrize("scenario", [
    "finished_order", "unfinished_order", "ties", "actual_finish_line",
    "common_clock", "same_tick_finish", "countdown_and_spawn", "reverse_and_jump",
    "immutable_finish", "recovery", "backward_recovery", "projection_noise",
    "rematches", "multiple_laps",
])
def test_production_race_results(result_policy_binary, scenario):
    subprocess.run([str(result_policy_binary), scenario], check=True)
