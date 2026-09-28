"""Recover a data-only course without executing the damaged preview application."""
import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def recover(source, destination, **kwargs):
    # Import inside the test: an absent implementation is a failing behavior test.
    module = importlib.import_module('burke_ez_preview.recover_preview_data')
    return module.recover_preview(source, destination, **kwargs)


def fixture_data():
    points = [
        {'x': 0, 'y': 0, 'lat': 0, 'lon': 0, 's': 0, 'heading_deg': 90, 'speed': 10},
        {'x': 10, 'y': 0, 'lat': 0, 'lon': 10/111320, 's': 10, 'heading_deg': 0, 'speed': 20},
        {'x': 10, 'y': 10, 'lat': 10/111320, 'lon': 10/111320, 's': 20, 'heading_deg': 270, 'speed': 30},
        {'x': 0, 'y': 10, 'lat': 10/111320, 'lon': 0, 's': 30, 'heading_deg': 180, 'speed': 40},
    ]
    return {'pack': 'fixture_ez', 'source_pack': 'fixture_original',
            'origin': {'lat': 0, 'lon': 0}, 'measured_length_m_ez': 40,
            'measured_length_m_src': 40, 'src_line': copy.deepcopy(points), 'ez_line': points,
            'gates': [{'name': 'Start/Finish', 'x': 0, 'y': 0, 's': 0, 'width_m': 29.7},
                      {'name': 'Corner', 'x': 10, 'y': 10, 's': 20, 'width_m': 24.3}],
            'buildings': [], 'water': [], 'shore': [], 'barriers': []}


def write_preview(tmp_path, data=None, tail=''):
    source = tmp_path / 'preview.html'
    source.write_text('<script>const DATA = ' + json.dumps(data or fixture_data()) + ';' + tail + '</script>', encoding='utf-8')
    return source


def test_recovers_geometry_speeds_gate_width_and_provenance(tmp_path):
    source = write_preview(tmp_path, tail='throw new Error("must never execute");')
    before = source.read_bytes()
    out = tmp_path / 'pack'
    report = recover(source, out)
    line = json.loads((out / 'racing_line.json').read_text())
    gates = json.loads((out / 'checkpoints.json').read_text())
    manifest = json.loads((out / 'manifest.json').read_text())
    assert source.read_bytes() == before
    assert len(line['samples']) == 4
    assert line['samples'][1]['target_speed_mps'] == 20
    assert line['samples'][2]['s_m'] == 20
    assert line['samples'][2]['lat'] == 10/111320
    assert gates['gates'][0]['width_m'] == 29.7
    assert gates['gates'][1]['lon'] == pytest.approx(10/111320)
    assert report['closed_length_m'] == pytest.approx(40)
    assert report['mean_target_speed_mps'] == pytest.approx(25)
    assert report['preview_sha256'] == hashlib.sha256(before).hexdigest()
    assert manifest['id'] == 'fixture_ez'
    assert manifest['certification']['status'] == 'provisional'
    assert manifest['file_hashes']['racing_line.json'] == hashlib.sha256((out / 'racing_line.json').read_bytes()).hexdigest()


@pytest.mark.parametrize('text', ['<html>no data</html>', 'const DATA = { broken;', 'const DATA = [];'])
def test_bad_preview_does_not_create_output(tmp_path, text):
    source = tmp_path / 'broken.html'
    source.write_text(text)
    out = tmp_path / 'pack'
    with pytest.raises(ValueError, match='broken.html'):
        recover(source, out)
    assert not out.exists()


@pytest.mark.parametrize('change', ['nan_coordinate', 'negative_speed', 'zero_width', 'path_id', 'length_disagrees'])
def test_invalid_course_is_rejected_before_writing(tmp_path, change):
    data = fixture_data()
    if change == 'nan_coordinate': data['ez_line'][0]['lat'] = float('nan')
    if change == 'negative_speed': data['ez_line'][0]['speed'] = -1
    if change == 'zero_width': data['gates'][0]['width_m'] = 0
    if change == 'path_id': data['pack'] = '../escape'
    if change == 'length_disagrees': data['measured_length_m_ez'] = 100
    source = write_preview(tmp_path, data)
    out = tmp_path / 'pack'
    with pytest.raises(ValueError): recover(source, out)
    assert not out.exists()


def test_existing_destination_is_never_overwritten(tmp_path):
    source = write_preview(tmp_path)
    out = tmp_path / 'pack'
    out.mkdir()
    existing = out / 'racing_line.json'
    existing.write_text('original user data')
    with pytest.raises(FileExistsError): recover(source, out)
    assert existing.read_text() == 'original user data'


def test_gate_distances_follow_ez_line_and_finish_closes_new_length(tmp_path):
    data = fixture_data()
    data['measured_length_m_src'] = 44
    data['gates'][1]['s'] = 22
    data['gates'].append({'name': 'Finish', 'x': 0, 'y': 0, 's': 44, 'width_m': 29.7})
    source = write_preview(tmp_path, data)
    out = tmp_path / 'pack'
    recover(source, out)
    gates = json.loads((out / 'checkpoints.json').read_text())['gates']
    assert gates[1]['source_s_m'] == 22
    assert gates[1]['s'] == pytest.approx(20)
    assert gates[-1]['source_s_m'] == 44
    assert gates[-1]['s'] == pytest.approx(40)
    assert gates[-1]['width_m'] == 29.7


def test_base_environment_dependencies_are_copied_and_hashed(tmp_path):
    source = write_preview(tmp_path)
    base = tmp_path / 'base'
    base.mkdir()
    (base / 'manifest.json').write_text(json.dumps({'id': 'fixture_original', 'skyline': 'skyline.json', 'environment': 'environment.json'}))
    (base / 'skyline.json').write_text('{"buildings": []}')
    (base / 'environment.json').write_text('{"offline": true}')
    out = tmp_path / 'pack'
    recover(source, out, base_pack=base)
    assert (out / 'skyline.json').read_bytes() == (base / 'skyline.json').read_bytes()
    manifest = json.loads((out / 'manifest.json').read_text())
    assert manifest['skyline'] == 'skyline.json'
    assert 'environment.json' in manifest['file_hashes']


def test_base_dependency_cannot_escape_pack(tmp_path):
    source = write_preview(tmp_path)
    base = tmp_path / 'base'
    base.mkdir()
    (base / 'manifest.json').write_text(json.dumps({'id': 'fixture_original', 'skyline': '../private.json'}))
    (tmp_path / 'private.json').write_text('{"unrelated": true}')
    with pytest.raises(ValueError, match='dependency'):
        recover(source, tmp_path / 'pack', base_pack=base)
    assert not (tmp_path / 'pack').exists()
