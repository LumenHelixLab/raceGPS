#!/usr/bin/env python3
"""Audit immutable inputs and route/road identity; not an OpenDRIVE validator."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/universal-city-compiler'))
from route_engine import directed_graph


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def audit(pack):
    pack = Path(pack).resolve()
    errors, warnings = [], []
    result = {'schema_version': 1, 'citypack': pack.name, 'errors': errors,
              'warnings': warnings, 'files': {}, 'status': 'failed',
              'scope': 'input integrity and explicit route connectivity; no Unreal or ASAM certification'}
    try:
        manifests = list(pack.glob('*_semantic_manifest.json'))
        if len(manifests) != 1:
            raise ValueError('Exactly one semantic manifest is required')
        manifest = json.loads(manifests[0].read_text())
        refs = dict(manifest.get('files', {}))
        for key in ('routes', 'road_graph', 'spawn_points', 'pois', 'buildings', 'gameplay_layer'):
            if key in manifest:
                refs[key] = manifest[key]
        if 'opendrive_file' in manifest:
            refs['xodr'] = manifest['opendrive_file']
        if manifest.get('release_ready') is False:
            errors.append('Manifest explicitly marks this pack as not release ready')
        paths = {}
        for key, filename in sorted(refs.items()):
            if not isinstance(filename, str):
                raise ValueError(f'Invalid file reference: {key}')
            path = (pack / filename).resolve()
            if not path.is_relative_to(pack):
                raise ValueError(f'File reference escapes citypack: {key}')
            if not path.is_file():
                errors.append(f'Missing declared file: {filename}')
                continue
            paths[key] = path
            result['files'][filename] = digest(path)
            expected = manifest.get('sha256', {}).get(filename)
            if expected and expected != result['files'][filename]:
                errors.append(f'Hash mismatch: {filename}')
        for key in ('road_graph', 'xodr', 'routes', 'spawn_points', 'buildings'):
            if key not in paths:
                errors.append(f'Required runtime input unavailable: {key}')
        if not manifest.get('sha256'):
            warnings.append('Legacy manifest has no pinned output hashes')
        graph = json.loads(paths['road_graph'].read_text()) if 'road_graph' in paths else {'roads': []}
        road_ids = {str(r['id']) for r in graph['roads']}
        result['road_count'] = len(graph['roads'])
        if not road_ids:
            errors.append('Road graph is empty')
        if len(road_ids) != len(graph['roads']):
            errors.append('Duplicate road IDs')
        if 'xodr' in paths:
            xml = ET.parse(paths['xodr']).getroot()
            if xml.tag != 'OpenDRIVE':
                errors.append('Road file root is not OpenDRIVE')
            xids = {r.get('id') for r in xml.findall('road')}
            result['xodr_road_count'] = len(xids)
            result['road_identity_difference'] = {
                'graph_only_count': len(road_ids - xids), 'xodr_only_count': len(xids - road_ids),
                'graph_only_sample': sorted(road_ids - xids)[:10], 'xodr_only_sample': sorted(xids - road_ids)[:10]}
            if road_ids != xids:
                errors.append('Road graph and OpenDRIVE have different source road identities')
        # Road components are diagnostic: disconnected geography is not itself a
        # failure. Every selected race must prove its own traversable sequence.
        parent = {rid: rid for rid in road_ids}
        def find(rid):
            while parent[rid] != rid:
                parent[rid] = parent[parent[rid]]
                rid = parent[rid]
            return rid
        for junction in graph.get('intersections', []):
            ids = list(map(str, junction.get('road_ids', [])))
            if any(rid not in parent for rid in ids):
                errors.append('Intersection references absent road')
                continue
            for rid in ids[1:]:
                parent[find(rid)] = find(ids[0])
        components = {}
        for rid in road_ids:
            key = find(rid)
            components[key] = components.get(key, 0) + 1
        result['component_sizes'] = sorted(components.values(), reverse=True)
        routes = json.loads(paths['routes'].read_text()) if 'routes' in paths else []
        if not isinstance(routes, list):
            routes = routes.get('routes', [])
        result['route_count'] = len(routes)
        if not routes:
            errors.append('No playable routes')
        if routes:
            adjacency, vertices = directed_graph(graph)
            edge_lookup = {(e['road_id'], e['segment_index'], e['direction']): (a, b)
                           for a, entries in adjacency.items() for b, e in entries}
            for route in routes:
                rid = route.get('route_id', route.get('id', 'unknown'))
                segments = route.get('segments', [])
                if not segments:
                    errors.append(f'Route {rid}: no explicit source-segment certificate')
                    continue
                walk = []
                for segment in segments:
                    edge = edge_lookup.get((str(segment['road_id']), segment['segment_index'], segment['direction']))
                    if edge is None or (walk and walk[-1] != edge[0]):
                        errors.append(f'Route {rid}: illegal or disconnected segment')
                        walk = []
                        break
                    if not walk:
                        walk.append(edge[0])
                    walk.append(edge[1])
                if walk and route.get('points') != [vertices[node] for node in walk]:
                    errors.append(f'Route {rid}: points differ from source-segment certificate')
                if walk and route.get('mode') == 'circuit' and (walk[0] != walk[-1] or len(walk) < 4):
                    errors.append(f'Route {rid}: circuit is not closed')
        if 'spawn_points' in paths:
            spawns = json.loads(paths['spawn_points'].read_text())
            if not spawns:
                errors.append('No spawn points')
        result['status'] = 'passed' if not errors else 'failed'
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        errors.append(str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('citypack', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = audit(args.citypack)
    text = json.dumps(report, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
