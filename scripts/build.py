#!/usr/bin/env python3
"""Build/cook/archive with a matching Unreal installation and retained evidence.

--check verifies prerequisites only. A package is NOT proof of playable behavior.
Windows is the release target; other hosts remain developer conveniences.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
DEFAULT_PROJECT = ROOT / 'apps/unreal-akron-beta/raceGPSAkronBeta.uproject'
PLATFORMS = {'Windows': 'Win64', 'Linux': 'Linux', 'Darwin': 'Mac'}
CLEVELAND_PACK = Path('citypacks/cleveland/burke_gp_1997')
CLEVELAND_MAP = '/Game/Maps/Cleveland5_0KmWorld'
CLEVELAND_GAME = '/Script/raceGPSAkronBeta.ClevelandShowcaseGameMode'
CLEVELAND_FILES = {
    'xodr': 'cleveland_burke_gp.xodr', 'racing_line': 'racing_line.json',
    'checkpoints': 'checkpoints.json', 'metadata': 'metadata.json',
    'environment': 'environment.json', 'water': 'water.json',
    'skyline': 'skyline.json', 'track_dressing': 'track_dressing.json',
}


def find_engine(version, system):
    """Explicit overrides win; never silently select an older engine."""
    if os.environ.get('RACEGPS_UE_ROOT'):
        return Path(os.environ['RACEGPS_UE_ROOT'].strip('"')).expanduser()
    if os.environ.get('UE5_BUILD'):
        return Path(os.environ['UE5_BUILD'].strip('"')).parents[3]
    candidates = {
        'Windows': [Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / f'Epic Games/UE_{version}',
                    Path(f'D:/Epic Games/UE_{version}'), Path(f'D:/UE_{version}')],
        'Darwin': [Path(f'/Users/Shared/Epic Games/UE_{version}')],
        'Linux': [Path.home() / f'UnrealEngine_{version}', Path(f'/opt/UnrealEngine_{version}')],
    }
    return next((p for p in candidates.get(system, []) if (p / 'Engine/Build/Build.version').is_file()), None)


def preflight(project, engine, system):
    if system not in PLATFORMS:
        raise ValueError(f'Unsupported build host: {system}')
    metadata = json.loads(project.read_text(encoding='utf-8-sig'))
    required = metadata.get('EngineAssociation')
    if not required or len(required.split('.')) != 2 or not all(v.isdigit() for v in required.split('.')):
        raise ValueError('Project must declare an explicit major.minor EngineAssociation for this build lane')
    engine = engine or find_engine(required, system)
    if engine is None:
        raise ValueError(f'Unreal {required} not found; pass --engine or set RACEGPS_UE_ROOT on the Unreal host')
    engine = engine.expanduser().resolve()
    version = json.loads((engine / 'Engine/Build/Build.version').read_text())
    actual = f"{version['MajorVersion']}.{version['MinorVersion']}"
    if actual != required:
        raise ValueError(f'Engine mismatch: project requires {required}, installation is {actual}')
    batch = engine / 'Engine/Build/BatchFiles'
    build = batch / ('Build.bat' if system == 'Windows' else f"{'Mac' if system == 'Darwin' else 'Linux'}/Build.sh")
    uat = batch / ('RunUAT.bat' if system == 'Windows' else 'RunUAT.sh')
    for tool in (build, uat):
        if not tool.is_file():
            raise ValueError(f'Required Unreal build tool is missing: {tool}')
    return engine, version, build, uat


def command_plan(project, build, uat, system, config, target, archive,
                 profile='all-semantic', max_parallel_actions=2):
    target_platform = PLATFORMS[system]
    if max_parallel_actions < 1:
        raise ValueError('max_parallel_actions must be positive')
    maps = f'-map={CLEVELAND_MAP}' if profile == 'cleveland-beta' else '-allmaps'
    return [
        [str(build), f'{target}Editor', target_platform, 'Development', f'-project={project}',
         '-waitmutex', f'-MaxParallelActions={max_parallel_actions}'],
        [str(uat), 'BuildCookRun', f'-project={project}', f'-target={target}',
         f'-platform={target_platform}', f'-clientconfig={config}', '-noP4',
         '-build', '-cook', maps, '-stage', '-pak', '-package', '-prereqs',
         f'-ubtargs=-MaxParallelActions={max_parallel_actions}',
         '-archive', f'-archivedirectory={archive}'],
    ]


def audit_cleveland_pack(source_root):
    """Validate the exact loose-file contract consumed by the Cleveland runtime."""
    pack = (source_root / CLEVELAND_PACK).resolve()
    report = {'citypack': 'cleveland/burke_gp_1997', 'status': 'failed', 'errors': [],
              'warnings': [], 'files': {},
              'scope': 'Cleveland runtime input integrity; no Unreal playtest or historical certification'}
    try:
        manifest = json.loads((pack / 'manifest.json').read_text(encoding='utf-8-sig'))
        if manifest.get('id') != 'cleveland_burke_gp_1997':
            raise ValueError('Unexpected Cleveland manifest id')
        documents = {}
        for key, filename in CLEVELAND_FILES.items():
            # Consumers load these names directly, rather than following arbitrary refs.
            if manifest.get(key) != filename:
                report['errors'].append(f'Invalid {key} reference; runtime requires {filename}')
            path = (pack / filename).resolve()
            if not path.is_relative_to(pack) or not path.is_file():
                report['errors'].append(f'Missing or external required file: {filename}')
                continue
            with path.open('rb') as stream:
                report['files'][filename] = hashlib.file_digest(stream, 'sha256').hexdigest()
            if path.suffix == '.json':
                documents[key] = json.loads(path.read_text(encoding='utf-8-sig'))
                if not isinstance(documents[key], dict):
                    raise ValueError(f'Expected JSON object: {filename}')
            elif ET.parse(path).getroot().tag != 'OpenDRIVE':
                raise ValueError(f'Expected OpenDRIVE root: {filename}')
        if report['errors']:
            return report
        line = documents['racing_line']
        samples = line.get('samples', [])
        if line.get('closed') is not True or len(samples) < 2:
            raise ValueError('racing_line.json must contain a closed sampled course')
        previous_s = -1.0
        for sample in samples:
            values = [sample.get(key) for key in ('lat', 'lon', 's')]
            if not all(isinstance(value, (int, float)) and not isinstance(value, bool)
                       and math.isfinite(value) for value in values):
                raise ValueError('racing_line.json contains non-finite or missing coordinates/distance')
            if values[2] < previous_s:
                raise ValueError('racing_line.json distances must be ordered')
            previous_s = values[2]
        if previous_s <= 0:
            raise ValueError('racing_line.json has no course length')
        gates = documents['checkpoints'].get('gates', [])
        distances = [gate.get('s') for gate in gates]
        if len(gates) < 2 or not all(isinstance(s, (int, float)) and math.isfinite(s) for s in distances):
            raise ValueError('checkpoints.json must contain ordered finite gates')
        if distances != sorted(distances):
            raise ValueError('checkpoints.json gates are out of order')
        if documents['environment'].get('offline') is not True:
            raise ValueError('Cleveland beta requires an offline environment')
        with (pack / 'manifest.json').open('rb') as stream:
            report['files']['manifest.json'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        report['warnings'].append('Course metadata remains provisional; historical certification is not claimed')
        report['status'] = 'passed'
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ET.ParseError) as error:
        report['errors'].append(str(error))
    return report


def stage_runtime_data(source_root, archive, project_name, target, system, profile='all-semantic'):
    """Stage loose inputs exactly where cooked ResolveCityLayout looks."""
    platform_dir = {'Windows': 'Windows', 'Linux': 'Linux', 'Darwin': 'Mac'}[system]
    packaged_project = archive / platform_dir / project_name
    if system == 'Windows':
        if not any(archive.rglob(f'{target}*.exe')):
            raise ValueError('UAT returned success without a game executable in the fresh archive')
        if profile == 'cleveland-beta' and not (archive / platform_dir / f'{target}.exe').is_file():
            raise ValueError(f'Cleveland launch executable is missing: {platform_dir}/{target}.exe')
        paks = packaged_project / 'Content/Paks'
        if not paks.is_dir() or not any(p.suffix in {'.pak', '.utoc'} for p in paks.iterdir()):
            raise ValueError('UAT returned success without expected cooked content')
    if not packaged_project.is_dir():
        raise ValueError(f'Expected packaged project directory is missing: {packaged_project}')
    if profile == 'cleveland-beta':
        report = audit_cleveland_pack(source_root)
        if report['status'] != 'passed':
            raise ValueError('Cleveland runtime data invalid: ' + '; '.join(report['errors']))
        destination = packaged_project / CLEVELAND_PACK
        destination.mkdir(parents=True, exist_ok=True)
        for filename in report['files']:
            shutil.copy2(source_root / CLEVELAND_PACK / filename, destination / filename)
        # Loaders use ProjectDir/citypacks; no source checkout or junction is needed.
        if system == 'Windows':
            launcher = archive / platform_dir / 'Play-raceGPS.bat'
            launcher.write_text(
                '@echo off\nsetlocal\ncd /d "%~dp0"\n'
                f'"%~dp0{target}.exe" "{CLEVELAND_MAP}?game={CLEVELAND_GAME}" '
                '-ClevelandPreset=Sunset -windowed -ResX=1600 -ResY=900\n'
                'exit /b %errorlevel%\n', encoding='utf-8', newline='\r\n')
        return
    packs = source_root / 'citypacks'
    if not list(packs.glob('*/*_semantic_manifest.json')):
        raise ValueError('No semantic citypack manifests to stage')
    for pack in sorted(packs.iterdir()):
        if pack.is_dir() and list(pack.glob('*_semantic_manifest.json')):
            shutil.copytree(pack, packaged_project / 'citypacks' / pack.name)
    specs = list((source_root / 'generated').glob('*_LevelSpec.json'))
    if not specs:
        raise ValueError('No generated level specifications to stage')
    destination = packaged_project / 'generated'
    destination.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        shutil.copy2(spec, destination / spec.name)


def validate_runtime_data(source_root, profile='all-semantic'):
    if profile == 'cleveland-beta':
        return [audit_cleveland_pack(source_root)]
    from citypack_audit import audit
    manifests = sorted((source_root / 'citypacks').glob('*/*_semantic_manifest.json'))
    if not manifests:
        raise ValueError('No semantic citypack manifests available')
    reports = [audit(manifest.parent) for manifest in manifests]
    return reports


def artifact_hashes(archive):
    result = {}
    for path in sorted(archive.rglob('*')):
        if path.is_file():
            with path.open('rb') as stream:
                result[path.relative_to(archive).as_posix()] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', '-e', type=Path)
    parser.add_argument('--project', '-p', type=Path, default=DEFAULT_PROJECT)
    parser.add_argument('--config', '-c', choices=['Development', 'Shipping', 'Test'], default='Development')
    parser.add_argument('--target', '-t', default='raceGPSAkronBeta')
    parser.add_argument('--profile', choices=['all-semantic', 'cleveland-beta'], default='all-semantic',
                        help='Explicit course payload; cleveland-beta is the two-car release lane')
    parser.add_argument('--max-parallel-actions', type=int, default=2,
                        help='Limit Unreal compiler parallelism to reduce peak RAM (default: 2)')
    parser.add_argument('--archive', type=Path, help='Fresh output directory; non-empty destinations are rejected')
    parser.add_argument('--report', type=Path, help='JSON evidence report (logs saved alongside it)')
    parser.add_argument('--check', action='store_true', help='Preflight only; does not compile or write game sources')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    report_path = (args.report or project.parent / 'Saved/BuildEvidence' / f'{stamp}.json').resolve()
    system = platform.system()
    archive = (args.archive or project.parent / 'Build' / ('Windows' if system == 'Windows' else system) / stamp).resolve()
    report = {'schema_version': 1, 'started_at': stamp, 'project': str(project),
              'host': system, 'python': platform.python_version(), 'configuration': args.config,
              'profile': args.profile, 'max_parallel_actions': args.max_parallel_actions,
              'archive': str(archive), 'status': 'failed', 'steps': [], 'play_tested': False}
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        commit = subprocess.run(['git', '-C', str(project.parent), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=False)
        report['source_commit'] = commit.stdout.strip() if commit.returncode == 0 else None
        dirty = subprocess.run(['git', '-C', str(project.parent), 'status', '--porcelain'], capture_output=True, text=True, check=False)
        report['source_dirty'] = bool(dirty.stdout.strip()) if dirty.returncode == 0 else None
        engine, version, build, uat = preflight(project, args.engine, system)
        report.update(engine=str(engine), engine_version=version)
        commands = command_plan(project, build, uat, system, args.config, args.target, archive,
                                args.profile, args.max_parallel_actions)
        report['planned_commands'] = commands
        if args.check:
            report['status'] = 'preflight_passed_build_not_run'
        else:
            if archive.exists() and any(archive.iterdir()):
                raise ValueError('Archive must be empty: use a fresh --archive to avoid accepting stale artifacts')
            report['citypack_audits'] = validate_runtime_data(project.parent.parent.parent, args.profile)
            if any(item['status'] != 'passed' for item in report['citypack_audits']):
                raise ValueError('Runtime citypack integrity failed; see citypack_audits in the evidence report')
            for index, command in enumerate(commands, 1):
                log = report_path.with_suffix(f'.step{index}.log')
                print(f'Running step {index}; log: {log}', flush=True)
                with log.open('w', encoding='utf-8') as output:
                    result = subprocess.run(command, cwd=project.parent, stdout=output, stderr=subprocess.STDOUT, check=False)
                report['steps'].append({'command': command, 'exit_code': result.returncode, 'log': str(log)})
                if result.returncode:
                    raise ValueError(f'Build step {index} failed ({result.returncode}); see {log}')
            stage_runtime_data(project.parent.parent.parent, archive, project.stem, args.target, system, args.profile)
            report['sha256'] = artifact_hashes(archive)
            report['status'] = 'packaged_not_play_tested'
        print(report['status'])
        return 0
    except (OSError, ValueError, KeyError, IndexError) as error:
        report['error'] = str(error)
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    finally:
        report['finished_at'] = datetime.now(UTC).isoformat()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(f'Evidence: {report_path}')


if __name__ == '__main__':
    sys.exit(main())
