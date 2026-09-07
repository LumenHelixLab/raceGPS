"""Independent vectors plus actual compiled C++/Python frame conformance.

This compiles the production math header; it does not compile Unreal/UHT.
"""
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from geo_frame import geo_to_unreal, to_unreal, compass_to_yaw, require_world_frame, WORLD_FRAME


@pytest.fixture(scope='module')
def cpp(tmp_path_factory):
    compiler = shutil.which('g++') or shutil.which('clang++')
    if not compiler:
        pytest.skip('C++ compiler unavailable; Unreal and native conformance remain unverified')
    exe = tmp_path_factory.mktemp('native-frame')/'frame-probe'
    result = subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
        '-I'+str(ROOT/'apps/unreal-akron-beta/Source/raceGPSAkronBeta/Public'),
        str(ROOT/'tests/cpp/geo_frame_probe.cpp'), '-o', str(exe)],capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    def run(text):
        result = subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True)
        return [[float(v) for v in line.split()] for line in result.stdout.splitlines()]
    return run


def test_metric_control_vectors_and_cpp(cpp):
    expected = [[10000,0,0],[0,-10000,0],[0,0,700]]
    assert cpp('l 100 0 0\nl 0 100 0\nl 0 0 7\n') == expected
    assert list(to_unreal(100,0).values()) == expected[0]
    assert list(to_unreal(0,100).values()) == expected[1]
    assert list(to_unreal(0,0,7).values()) == expected[2]


def test_road_width_is_700_cm(cpp):
    left,right = cpp('l 0 -3.5 0\nl 0 3.5 0\n')
    assert math.dist(left,right) == 700


def test_cardinal_headings_and_wrap(cpp):
    headings = [0,90,180,270,360,-90]
    expected = [-90,0,90,-180,-90,-180]
    assert [compass_to_yaw(h) for h in headings] == expected
    assert [v[0] for v in cpp(''.join(f'y {h}\n' for h in headings))] == expected


def test_xodr_line_keeps_final_endpoint(cpp):
    assert cpp('e 10 20 0 100\n')[0] == [11000,-2000,0]
    assert cpp(f'e 10 20 {math.pi/2} 100\n')[0] == pytest.approx([1000,-12000,0])


def test_geographic_origin_and_millimeter_precision(cpp):
    lat,lon = 41.5178611,-81.6826389
    data = [(lat,lon),(lat+1.e-8,lon),(lat,lon+0.00001)]
    rows = cpp(''.join(f'g {a:.12f} {b:.12f} {lat:.12f} {lon:.12f}\n' for a,b in data))
    assert rows[0] == [0,0,0]
    assert rows[1][1] == pytest.approx(-0.11132,abs=0.00001)
    for (a,b),result in zip(data,rows):
        assert result == pytest.approx(list(geo_to_unreal(a,b,lat,lon).values()),abs=1.e-6)


@pytest.mark.parametrize('doc',[{}, {'coordinate_frame':'legacy-xz-m'}, {'coordinate_frame':'unknown'}])
def test_unknown_scene_frame_rejected(doc):
    with pytest.raises(ValueError,match='regenerate'):
        require_world_frame(doc)


def test_levelspec_bounding_volumes_use_horizontal_xy():
    spec = importlib.util.spec_from_file_location('levelspec_v3',ROOT/'tools/generate-level-spec.py')
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    volumes = mod.generate_traffic_volumes([{'route_id':'north','points':[{'lat':0,'lon':0},{'lat':0.001,'lon':0}]}],0,0)
    bounds=volumes[0]['bounds']
    assert bounds['min']['y'] < -11132 < bounds['max']['y']
    assert bounds['min']['z'] == -1000 and bounds['max']['z'] == 3000


def test_old_spec_rejected_before_editor_import(tmp_path):
    path = tmp_path/'old.json';path.write_text(json.dumps({'spawn_points':[]}))
    result=subprocess.run([sys.executable,str(ROOT/'tools/ue5-import-level-spec.py'),'--spec',str(path)],capture_output=True,text=True)
    assert result.returncode != 0 and 'regenerate' in result.stderr
    assert 'spawn_actor_from_class' not in result.stdout


def test_scene_tags_bind_world_frame_and_origin():
    from geo_frame import scene_tags
    tags=scene_tags({'coordinate_frame':WORLD_FRAME,'origin':{'lat':41.5178611,'lon':-81.6826389}})
    assert tags == ['racegps.frame:racegps-ue-esu-cm-v1','racegps.origin.lat=41.517861100','racegps.origin.lon=-81.682638900']
    with pytest.raises(ValueError):
        scene_tags({'coordinate_frame':WORLD_FRAME,'origin':{'lat':float('nan'),'lon':0}})


def test_invalid_geographic_values_are_rejected():
    for values in [(float('nan'),0,0,0),(0,0,90,0),(0,181,0,0)]:
        with pytest.raises(ValueError):
            geo_to_unreal(*values)
