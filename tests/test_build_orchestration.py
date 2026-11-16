"""Executable fake-tool tests: validate orchestration, never Unreal behavior."""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

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


@pytest.fixture
def cleveland_source(fixture):
    root, project, engine, batch = fixture
    source = Path(__file__).resolve().parents[1] / 'citypacks/cleveland/burke_gp_1997'
    shutil.copytree(source, root / 'citypacks/cleveland/burke_gp_1997')
    return root, project, engine, batch


def test_cleveland_release_selects_its_own_payload(cleveland_source, tmp_path):
    root, _, _, _ = cleveland_source
    # An unrelated, unfinished city must not block the explicitly selected course.
    (root / 'citypacks/test-city/buildings.json').unlink()
    reports = build.validate_runtime_data(root, profile='cleveland-beta')
    assert len(reports) == 1
    assert reports[0]['status'] == 'passed', reports
    assert reports[0]['citypack'] == 'cleveland/burke_gp_1997'
    assert 'racing_line.json' in reports[0]['files']

    archive = tmp_path / 'release'
    app = archive / 'Windows/Game'
    (app / 'Content/Paks').mkdir(parents=True)
    (app / 'Content/Paks/Game.pak').write_bytes(b'fixture only')
    (archive / 'Windows/Game.exe').write_bytes(b'fixture only')
    build.stage_runtime_data(root, archive, 'Game', 'Game', 'Windows', profile='cleveland-beta')
    shipped = app / 'citypacks/cleveland/burke_gp_1997'
    assert (shipped / 'racing_line.json').read_bytes() == (root / 'citypacks/cleveland/burke_gp_1997/racing_line.json').read_bytes()
    assert (shipped / 'track_dressing.json').is_file()
    assert not (app / 'citypacks/test-city').exists()
    launcher = (archive / 'Windows/Play-raceGPS.bat').read_text()
    assert 'Game.exe' in launcher
    assert '/Game/Maps/Cleveland5_0KmWorld?game=/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode' in launcher
    assert '-ClevelandPreset=Sunset' in launcher
    assert '-ClevelandAutoLap' not in launcher


@pytest.mark.parametrize('filename', ['racing_line.json', 'checkpoints.json', 'skyline.json', 'track_dressing.json'])
def test_cleveland_release_rejects_missing_course_inputs(cleveland_source, filename):
    root, _, _, _ = cleveland_source
    (root / 'citypacks/cleveland/burke_gp_1997' / filename).unlink()
    report = build.validate_runtime_data(root, profile='cleveland-beta')[0]
    assert report['status'] == 'failed'
    assert any(filename in error for error in report['errors'])


def test_cleveland_release_rejects_manifest_path_escape(cleveland_source):
    root, _, _, _ = cleveland_source
    manifest_path = root / 'citypacks/cleveland/burke_gp_1997/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['racing_line'] = '../../../outside.json'
    manifest_path.write_text(json.dumps(manifest))
    report = build.validate_runtime_data(root, profile='cleveland-beta')[0]
    assert report['status'] == 'failed'
    assert any('racing_line' in error for error in report['errors'])


def test_cleveland_commands_cook_selected_map_and_limit_memory(fixture, tmp_path):
    _, project, _, batch = fixture
    commands = build.command_plan(project, batch / 'Build.bat', batch / 'RunUAT.bat',
        'Windows', 'Development', 'Game', tmp_path, profile='cleveland-beta', max_parallel_actions=2)
    assert '-MaxParallelActions=2' in commands[0]
    assert '-ubtargs=-MaxParallelActions=2' in commands[1]
    assert '-map=/Game/Maps/Cleveland5_0KmWorld' in commands[1]
    assert '-allmaps' not in commands[1]


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX fake executables, not a Windows/Unreal test')
def test_cleveland_cli_runs_selected_build_and_stages_without_unrelated_city(cleveland_source, monkeypatch, tmp_path):
    root, project, engine, batch = cleveland_source
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    (root / 'citypacks/test-city/buildings.json').unlink()
    archive = tmp_path / 'beta archive'
    arguments = tmp_path / 'beta args.txt'
    (batch / 'RunUAT.sh').write_text(
        f'#!/bin/sh\nprintf "%s\\n" "$@" > "{arguments}"\nmkdir -p "{archive}/Linux/Game"\n')
    report_path = tmp_path / 'beta.json'
    assert build.main(['--profile', 'cleveland-beta', '--project', str(project),
        '--engine', str(engine), '--target', 'Game', '--archive', str(archive),
        '--report', str(report_path)]) == 0
    arguments = arguments.read_text().splitlines()
    assert '-map=/Game/Maps/Cleveland5_0KmWorld' in arguments
    assert '-ubtargs=-MaxParallelActions=2' in arguments
    data = json.loads(report_path.read_text())
    assert data['profile'] == 'cleveland-beta'
    assert data['status'] == 'packaged_not_play_tested'
    assert not data['play_tested']
    assert len(data['citypack_audits']) == 1
    assert 'Linux/Game/citypacks/cleveland/burke_gp_1997/racing_line.json' in data['sha256']


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX fake executables, not a Windows/Unreal test')
def test_cleveland_missing_payload_stops_before_any_build(cleveland_source, monkeypatch, tmp_path):
    root, project, engine, _ = cleveland_source
    monkeypatch.setattr(build.platform, 'system', lambda: 'Linux')
    (root / 'citypacks/cleveland/burke_gp_1997/checkpoints.json').unlink()
    report_path = tmp_path / 'missing-course.json'
    assert build.main(['--profile', 'cleveland-beta', '--project', str(project),
        '--engine', str(engine), '--report', str(report_path)]) == 1
    data = json.loads(report_path.read_text())
    assert data['steps'] == []
    assert not data['play_tested']
    assert data['citypack_audits'][0]['status'] == 'failed'


def test_cleveland_rejects_archive_without_its_launch_executable(cleveland_source, tmp_path):
    root, _, _, _ = cleveland_source
    archive = tmp_path / 'inner-only'
    app = archive / 'Windows/Game'
    (app / 'Content/Paks').mkdir(parents=True)
    (app / 'Content/Paks/Game.pak').write_bytes(b'fixture only')
    inner = app / 'Binaries/Win64/Game-Win64-Development.exe'
    inner.parent.mkdir(parents=True)
    inner.write_bytes(b'fixture only')
    with pytest.raises(ValueError, match='launch executable'):
        build.stage_runtime_data(root, archive, 'Game', 'Game', 'Windows', profile='cleveland-beta')
