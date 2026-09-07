"""Executable fake-tool tests: validate orchestration, never Unreal behavior."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

spec = importlib.util.spec_from_file_location('racegps_build', Path(__file__).resolve().parents[1] / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    monkeypatch.delenv('UE5_BUILD', raising=False)
    monkeypatch.delenv('RACEGPS_UE_ROOT', raising=False)
    root = tmp_path / 'repo with spaces'
    project = root / 'apps/game/Game.uproject'
    project.parent.mkdir(parents=True)
    project.write_text(json.dumps({'EngineAssociation': '5.7'}))
    engine = tmp_path / 'Epic Engine'
    version = engine / 'Engine/Build/Build.version'
    version.parent.mkdir(parents=True)
    version.write_text(json.dumps({'MajorVersion': 5, 'MinorVersion': 7, 'PatchVersion': 0}))
    batch = engine / 'Engine/Build/BatchFiles'
    (batch / 'Linux').mkdir(parents=True)
    for path in (batch / 'Linux/Build.sh', batch / 'RunUAT.sh', batch / 'Build.bat', batch / 'RunUAT.bat'):
        path.write_text('#!/bin/sh\nexit 0\n')
        path.chmod(0o755)
    pack = root / 'citypacks/test-city'
    pack.mkdir(parents=True)
    points = [{'lat':41.0,'lon':-81.0},{'lat':41.01,'lon':-81.0}]
    files = {'road_graph':'graph.json','routes':'routes.json','spawn_points':'spawns.json','buildings':'buildings.json','xodr':'test.xodr'}
    (pack / 'test_semantic_manifest.json').write_text(json.dumps({'files': files}))
    (pack / 'graph.json').write_text(json.dumps({'roads':[{'id':'1','points':points}], 'intersections':[]}))
    (pack / 'routes.json').write_text(json.dumps([{'route_id':'fixture','points':points,
        'segments':[{'road_id':'1','segment_index':0,'direction':1}]}]))
    (pack / 'spawns.json').write_text('[{"lat":41,"lon":-81}]')
    (pack / 'buildings.json').write_text('{"buildings":[]}')
    (pack / 'test.xodr').write_text('<OpenDRIVE><road id="1"/></OpenDRIVE>')
    (root / 'generated').mkdir()
    (root / 'generated/Test_LevelSpec.json').write_text('{}')
    return root, project, engine, batch


def test_engine_mismatch_rejected_even_with_explicit_path(fixture):
    _, project, engine, _ = fixture
    (engine / 'Engine/Build/Build.version').write_text('{"MajorVersion":5,"MinorVersion":5}')
    with pytest.raises(ValueError, match='Engine mismatch'):
        build.preflight(project, engine, 'Windows')


def test_missing_tool_fails_preflight(fixture):
    _, project, engine, batch = fixture
    (batch / 'RunUAT.bat').unlink()
    with pytest.raises(ValueError, match='build tool is missing'):
        build.preflight(project, engine, 'Windows')


def test_legacy_quoted_override_is_resolved_to_engine_root(fixture, monkeypatch):
    _, _, engine, batch = fixture
    monkeypatch.setenv('UE5_BUILD', f'"{batch / "Build.bat"}"')
    assert build.find_engine('5.7', 'Windows') == engine


def test_check_has_no_build_side_effects(fixture, monkeypatch, tmp_path):
    _, project, engine, _ = fixture
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    report = tmp_path / 'check.json'
    before = sorted(p.relative_to(project.parent) for p in project.parent.rglob('*'))
    assert build.main(['--check', '--project', str(project), '--engine', str(engine), '--report', str(report)]) == 0
    data = json.loads(report.read_text())
    assert data['status'] == 'preflight_passed_build_not_run'
    assert data['steps'] == [] and not data['play_tested']
    assert before == sorted(p.relative_to(project.parent) for p in project.parent.rglob('*'))


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX fake executables, not a Windows/Unreal test')
def test_failed_editor_stops_uat_and_preserves_log(fixture, monkeypatch, tmp_path):
    _, project, engine, batch = fixture
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    (batch / 'Linux/Build.sh').write_text('#!/bin/sh\necho EDITOR_FAILED\nexit 17\n')
    marker = tmp_path / 'uat-ran'
    (batch / 'RunUAT.sh').write_text(f'#!/bin/sh\ntouch "{marker}"\n')
    report = tmp_path / 'build.json'
    assert build.main(['--project', str(project), '--engine', str(engine), '--report', str(report)]) == 1
    data = json.loads(report.read_text())
    assert data['steps'][0]['exit_code'] == 17
    assert 'EDITOR_FAILED' in Path(data['steps'][0]['log']).read_text()
    assert not marker.exists()
    assert data['status'] == 'failed'


def test_stale_archive_rejected_before_any_build(fixture, monkeypatch, tmp_path):
    _, project, engine, _ = fixture
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    archive = tmp_path / 'archive'
    archive.mkdir()
    (archive / 'stale.exe').write_bytes(b'stale')
    report = tmp_path / 'build.json'
    assert build.main(['--project', str(project), '--engine', str(engine), '--archive', str(archive), '--report', str(report)]) == 1
    data = json.loads(report.read_text())
    assert 'Archive must be empty' in data['error']
    assert data['steps'] == []


def test_windows_package_must_contain_game_and_cooked_content(fixture, tmp_path):
    root, _, _, _ = fixture
    archive = tmp_path / 'archive'
    with pytest.raises(ValueError, match='game executable'):
        build.stage_runtime_data(root, archive, 'Game', 'Game', 'Windows')
    app = archive / 'Windows/Game'
    app.mkdir(parents=True)
    (archive / 'Windows/Game.exe').write_bytes(b'fixture only')
    with pytest.raises(ValueError, match='cooked content'):
        build.stage_runtime_data(root, archive, 'Game', 'Game', 'Windows')
    (app / 'Content/Paks').mkdir(parents=True)
    (app / 'Content/Paks/Game.pak').write_bytes(b'fixture only')
    build.stage_runtime_data(root, archive, 'Game', 'Game', 'Windows')
    assert (app / 'citypacks/test-city/test.xodr').read_text() == '<OpenDRIVE><road id="1"/></OpenDRIVE>'
    assert (app / 'generated/Test_LevelSpec.json').is_file()
    assert 'Windows/Game/citypacks/test-city/test.xodr' in build.artifact_hashes(archive)


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX fake executables, not a Windows/Unreal test')
def test_successful_fake_tools_retain_commands_and_do_not_claim_playtest(fixture, monkeypatch, tmp_path):
    _, project, engine, batch = fixture
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    archive = tmp_path / 'archive with spaces'
    # Record exact argv, exercising real subprocess path/space handling.
    arguments = tmp_path / 'args.txt'
    (batch / 'RunUAT.sh').write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > "{arguments}"\nmkdir -p "{archive}/Linux/Game"\n')
    report = tmp_path / 'build.json'
    assert build.main(['--project', str(project), '--engine', str(engine), '--target', 'Game', '--archive', str(archive), '--report', str(report)]) == 0
    lines = arguments.read_text().splitlines()
    assert f'-project={project}' in lines
    assert '-build' in lines and '-cook' in lines
    data = json.loads(report.read_text())
    assert data['status'] == 'packaged_not_play_tested'
    assert len(data['steps']) == 2 and data['play_tested'] is False


def test_mac_commands_use_mac_not_linux(fixture, tmp_path):
    _, project, _, batch = fixture
    commands = build.command_plan(project, batch / 'Mac/Build.sh', batch / 'RunUAT.sh', 'Darwin', 'Shipping', 'Game', tmp_path)
    assert commands[0][2] == 'Mac'
    assert '-platform=Mac' in commands[1]


def test_invalid_city_data_stops_before_editor_execution(fixture, monkeypatch, tmp_path):
    root, project, engine, _ = fixture
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    (root / 'citypacks/test-city/buildings.json').unlink()
    report = tmp_path / 'blocked.json'
    assert build.main(['--project', str(project), '--engine', str(engine), '--report', str(report)]) == 1
    data = json.loads(report.read_text())
    assert data['steps'] == []
    assert data['citypack_audits'][0]['status'] == 'failed'
