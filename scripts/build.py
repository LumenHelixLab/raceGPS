#!/usr/bin/env python3
"""Build/cook/archive with a matching Unreal installation and retained evidence.

--check verifies prerequisites only. A package is NOT proof of playable behavior.
Windows is the release target; other hosts remain developer conveniences.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / 'apps/unreal-akron-beta/raceGPSAkronBeta.uproject'
PLATFORMS = {'Windows': 'Win64', 'Linux': 'Linux', 'Darwin': 'Mac'}


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


def command_plan(project, build, uat, system, config, target, archive):
    target_platform = PLATFORMS[system]
    return [
        [str(build), f'{target}Editor', target_platform, 'Development', f'-project={project}', '-waitmutex'],
        [str(uat), 'BuildCookRun', f'-project={project}', f'-target={target}',
         f'-platform={target_platform}', f'-clientconfig={config}', '-noP4',
         '-build', '-cook', '-allmaps', '-stage', '-pak', '-package', '-prereqs',
         '-archive', f'-archivedirectory={archive}'],
    ]


def stage_runtime_data(source_root, archive, project_name, target, system):
    """Stage loose inputs exactly where cooked ResolveCityLayout looks."""
    platform_dir = {'Windows': 'Windows', 'Linux': 'Linux', 'Darwin': 'Mac'}[system]
    packaged_project = archive / platform_dir / project_name
    if system == 'Windows':
        if not any(archive.rglob(f'{target}*.exe')):
            raise ValueError('UAT returned success without a game executable in the fresh archive')
        paks = packaged_project / 'Content/Paks'
        if not paks.is_dir() or not any(p.suffix in {'.pak', '.utoc'} for p in paks.iterdir()):
            raise ValueError('UAT returned success without expected cooked content')
    if not packaged_project.is_dir():
        raise ValueError(f'Expected packaged project directory is missing: {packaged_project}')
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
    parser.add_argument('--archive', type=Path, help='Fresh output directory; non-empty destinations are rejected')
    parser.add_argument('--report', type=Path, help='JSON evidence report (logs saved alongside it)')
    parser.add_argument('--check', action='store_true', help='Preflight only; does not compile or write game sources')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report_path = (args.report or project.parent / 'Saved/BuildEvidence' / f'{stamp}.json').resolve()
    system = platform.system()
    archive = (args.archive or project.parent / 'Build' / ('Windows' if system == 'Windows' else system) / stamp).resolve()
    report = {'schema_version': 1, 'started_at': stamp, 'project': str(project),
              'host': system, 'python': platform.python_version(), 'configuration': args.config,
              'archive': str(archive), 'status': 'failed', 'steps': [], 'play_tested': False}
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        commit = subprocess.run(['git', '-C', str(project.parent), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        report['source_commit'] = commit.stdout.strip() if commit.returncode == 0 else None
        dirty = subprocess.run(['git', '-C', str(project.parent), 'status', '--porcelain'], capture_output=True, text=True)
        report['source_dirty'] = bool(dirty.stdout.strip()) if dirty.returncode == 0 else None
        engine, version, build, uat = preflight(project, args.engine, system)
        report.update(engine=str(engine), engine_version=version)
        commands = command_plan(project, build, uat, system, args.config, args.target, archive)
        report['planned_commands'] = commands
        if args.check:
            report['status'] = 'preflight_passed_build_not_run'
        else:
            if archive.exists() and any(archive.iterdir()):
                raise ValueError('Archive must be empty: use a fresh --archive to avoid accepting stale artifacts')
            for index, command in enumerate(commands, 1):
                log = report_path.with_suffix(f'.step{index}.log')
                print(f'Running step {index}; log: {log}', flush=True)
                with log.open('w', encoding='utf-8') as output:
                    result = subprocess.run(command, cwd=project.parent, stdout=output, stderr=subprocess.STDOUT)
                report['steps'].append({'command': command, 'exit_code': result.returncode, 'log': str(log)})
                if result.returncode:
                    raise ValueError(f'Build step {index} failed ({result.returncode}); see {log}')
            stage_runtime_data(project.parent.parent.parent, archive, project.stem, args.target, system)
            report['sha256'] = artifact_hashes(archive)
            report['status'] = 'packaged_not_play_tested'
        print(report['status'])
        return 0
    except (OSError, ValueError, KeyError, IndexError) as error:
        report['error'] = str(error)
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(f'Evidence: {report_path}')


if __name__ == '__main__':
    sys.exit(main())
