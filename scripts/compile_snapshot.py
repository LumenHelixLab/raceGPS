#!/usr/bin/env python3
"""Offline, hash-pinned context compiler. Does not invent a historical race route."""
import argparse
import importlib.util
import json
import re
import shutil
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from citypack_audit import digest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/universal-city-compiler'))
from road_network import build_road_graph
from building_extractor import extract_buildings
from export_bundle import export_bundle
_xodr_spec = importlib.util.spec_from_file_location('racegps_snapshot_xodr', ROOT / 'tools/akron-semantic-compiler/osm_to_xodr.py')
_xodr_module = importlib.util.module_from_spec(_xodr_spec)
_xodr_spec.loader.exec_module(_xodr_module)
generate_xodr = _xodr_module.generate_xodr


def compile_snapshot(source, source_record, output, city_id, origin):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}', city_id):
        raise ValueError('Use a stable lowercase city ID without path separators')
    metadata = json.loads(source_record.read_text())
    if metadata.get('sha256') != digest(source):
        raise ValueError('Source hash differs from the recorded snapshot')
    if not all(metadata.get(k) for k in ('url', 'retrieved_at', 'attribution', 'license_url')):
        raise ValueError('Source URL/date/attribution/license record required')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be a fresh directory; never overwrite a frozen snapshot')
    graph = build_road_graph(source, *origin)
    if not graph['roads']:
        raise ValueError('No road geometry in source')
    root = ET.parse(source).getroot()
    nodes = {n.get('id'): {'lat': float(n.get('lat')), 'lon': float(n.get('lon'))} for n in root.findall('node')}
    airfield = []
    for way in sorted(root.findall('way'), key=lambda w: w.get('id')):
        tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
        if tags.get('aeroway') not in ('runway', 'taxiway', 'apron'):
            continue
        ids = [n.get('ref') for n in way.findall('nd')]
        if any(n not in nodes for n in ids):
            raise ValueError(f'Incomplete aeroway {way.get("id")}')
        airfield.append({'osm_way_id': way.get('id'), 'tags': tags,
                         'node_ids': ids, 'points': [nodes[n] for n in ids]})
    output.mkdir(parents=True, exist_ok=True)
    buildings = extract_buildings(source, *origin)
    # Empty routes are intentional: airport aeroways are context, not a certified
    # 2006 course or a user-authored online route.
    manifest = export_bundle(output, city_id, graph['bounds'], [], [], buildings, graph)
    manifest['origin'] = graph['origin']
    manifest.update(release_ready=False, historical_course_certified=False,
                    source=metadata, generated_at=None,
                    limitations=['No historical racing line, control points or barriers certified',
                                 'No measured terrain or building facade reconstruction',
                                 'OpenDRIVE junction/lane semantics are prototype quality',
                                 'OSM relations/multipolygon coverage needs a separate completeness review',
                                 'Layer offsets are inferred; not measured bridge clearances'])
    generate_xodr(graph, output / f'{city_id}.xodr')
    (output / 'airfield.json').write_text(json.dumps(airfield, indent=2) + '\n')
    shutil.copyfile(source, output / 'source.osm')
    shutil.copyfile(source_record, output / 'source.json')
    manifest['files'].update(xodr=f'{city_id}.xodr', airfield='airfield.json', source='source.osm', source_record='source.json')
    manifest['sha256'] = {name: digest(output / name) for name in sorted(manifest['files'].values())}
    (output / f'{city_id}_semantic_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return {'status': 'context_compiled_not_race_ready', 'city_id': city_id,
            'roads': graph['road_count'], 'buildings': len(buildings), 'airfield_features': len(airfield),
            'output_sha256': manifest['sha256'], 'source_sha256': metadata['sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-record', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--city-id', required=True)
    parser.add_argument('--origin', type=float, nargs=2, metavar=('LAT', 'LON'), required=True)
    args = parser.parse_args()
    try:
        result = compile_snapshot(args.source, args.source_record, args.output, args.city_id, args.origin)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, ET.ParseError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
