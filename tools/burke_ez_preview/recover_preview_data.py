"""Recover the preview's embedded JSON as a traceable legacy Cleveland pack.

Does not evaluate JavaScript. The original preview and base pack are read-only.
Rounded preview coordinates are retained; derived curvature is explicitly marked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


def _number(obj: dict, key: str, *, minimum=None, maximum=None) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{key} must be a finite number')
    if minimum is not None and value < minimum:
        raise ValueError(f'{key} must be >= {minimum}')
    if maximum is not None and value > maximum:
        raise ValueError(f'{key} must be <= {maximum}')
    return float(value)


def _identifier(value) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', value):
        raise ValueError('pack identifier must contain only letters, digits, underscore or hyphen')
    return value


def _json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def _curvature(points: list, i: int) -> float:
    a, b, c = points[i-1], points[i], points[(i+1) % len(points)]
    ab = (b['x']-a['x'], b['y']-a['y'])
    bc = (c['x']-b['x'], c['y']-b['y'])
    ac = (c['x']-a['x'], c['y']-a['y'])
    denominator = math.hypot(*ab) * math.hypot(*bc) * math.hypot(*ac)
    return 2 * (ab[0]*bc[1]-ab[1]*bc[0]) / denominator if denominator > 1e-9 else 0.0


def _project_gate(points: list, x: float, y: float) -> tuple[float, float]:
    best_distance, best_s, accumulated = math.inf, 0.0, 0.0
    for a, b in zip(points, points[1:] + points[:1]):
        dx, dy = b['x']-a['x'], b['y']-a['y']
        length = math.hypot(dx, dy)
        alpha = max(0, min(1, ((x-a['x'])*dx+(y-a['y'])*dy)/(length*length))) if length else 0
        distance = math.hypot(x-a['x']-alpha*dx, y-a['y']-alpha*dy)
        if distance < best_distance:
            best_distance, best_s = distance, accumulated + alpha*length
        accumulated += length
    return best_s, best_distance


def recover_preview(source_html: Path, output_dir: Path, *, base_pack: Path | None = None) -> dict:
    source_html, output_dir = Path(source_html), Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f'refusing to overwrite {output_dir}')
    raw = source_html.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
        match = re.search(r'\bconst\s+DATA\s*=\s*', text)
        if not match:
            raise ValueError('missing const DATA JSON literal')
        data, _ = json.JSONDecoder().raw_decode(text[match.end():])
        if not isinstance(data, dict):
            raise ValueError('DATA must be a JSON object')
        pack_id = _identifier(data.get('pack'))
        source_id = _identifier(data.get('source_pack'))
        origin = data['origin']
        lat0 = _number(origin, 'lat', minimum=-90, maximum=90)
        lon0 = _number(origin, 'lon', minimum=-180, maximum=180)
        lon_scale = 111320.0 * math.cos(math.radians(lat0))
        if abs(lon_scale) < 1:
            raise ValueError('preview local frame cannot recover polar coordinates')
        points, gates = data['ez_line'], data['gates']
        if not isinstance(points, list) or len(points) < 3:
            raise ValueError('ez_line needs at least three samples')
        if not isinstance(gates, list) or len(gates) < 2:
            raise ValueError('gates needs at least two entries')
        previous_s = -1.0
        for point in points:
            for key in ('x', 'y', 'heading_deg'):
                _number(point, key)
            _number(point, 'lat', minimum=-90, maximum=90)
            _number(point, 'lon', minimum=-180, maximum=180)
            distance = _number(point, 's', minimum=0)
            _number(point, 'speed', minimum=0)
            if distance <= previous_s:
                raise ValueError('sample s must increase strictly')
            previous_s = distance
        closed_length = sum(math.hypot(b['x']-a['x'], b['y']-a['y'])
                            for a, b in zip(points, points[1:] + points[:1]))
        stated_length = _number(data, 'measured_length_m_ez', minimum=0.01)
        if abs(closed_length - stated_length) > 0.10:
            raise ValueError(f'closed length {closed_length:.3f} differs from accepted {stated_length:.3f}')
        gate_output = []
        previous_s = -1.0
        for i, gate in enumerate(gates):
            x, y = _number(gate, 'x'), _number(gate, 'y')
            width = _number(gate, 'width_m', minimum=0.01)
            source_distance = _number(gate, 's', minimum=0,
                                      maximum=_number(data, 'measured_length_m_src', minimum=0.01)+0.01)
            distance, offset = _project_gate(points, x, y)
            if offset > width / 2:
                raise ValueError(f'gate {i} lies outside its half-width from the EZ line')
            # First and duplicate final gate represent two visits to the same start plane.
            if i == 0 and source_distance == 0:
                distance = 0.0
            elif i == len(gates)-1 and math.hypot(x-gates[0]['x'], y-gates[0]['y']) < 0.01:
                distance = closed_length
            if distance <= previous_s:
                raise ValueError('gate s must increase strictly')
            previous_s = distance
            gate_output.append({'index': i, 'name': str(gate['name']),
                                'lat': lat0 + y/111320.0, 'lon': lon0 + x/lon_scale,
                                's': distance, 'source_s_m': source_distance, 'width_m': width})

        blobs = {}
        manifest = {'id': pack_id, 'display_name': 'Cleveland Burke EZ', 'engine': 'UE5',
                    'racing_line': 'racing_line.json', 'checkpoints': 'checkpoints.json',
                    'offline': True, 'carla_required': False, 'cesium_required': False}
        inherited = {}
        if base_pack is not None:
            base_pack = Path(base_pack).resolve()
            original = json.loads((base_pack / 'manifest.json').read_text(encoding='utf-8-sig'))
            if original.get('id') != source_id:
                raise ValueError('base pack identity does not match preview source_pack')
            for key in ('xodr', 'metadata', 'environment', 'water', 'skyline', 'track_dressing'):
                if key not in original:
                    continue
                name = original[key]
                if not isinstance(name, str) or Path(name).name != name or ':' in name or '\\' in name:
                    raise ValueError(f'unsafe dependency {key}: {name}')
                dependency = (base_pack / name).resolve()
                if dependency.parent != base_pack:
                    raise ValueError(f'dependency escapes base pack: {name}')
                blobs[name] = dependency.read_bytes()
                inherited[name] = hashlib.sha256(blobs[name]).hexdigest()
                manifest[key] = name
        samples = [{'lat': p['lat'], 'lon': p['lon'], 's_m': p['s'],
                    'heading_deg': p['heading_deg'], 'target_speed_mps': p['speed'],
                    'curvature': _curvature(points, i)} for i, p in enumerate(points)]
        blobs['racing_line.json'] = _json_bytes({
            'id': pack_id, 'closed': True, 'frame': 'wgs84', 'distance_unit': 'm',
            'measured_length_m': stated_length, 'origin': origin, 'samples': samples,
            'curvature_source': 'derived circumcircle curvature from rounded preview XY; not original curvature'})
        blobs['checkpoints.json'] = _json_bytes({'track_id': pack_id, 'lap_count': 1, 'gates': gate_output})
        report = {'schema_version': 1, 'pack_id': pack_id, 'source_pack_id': source_id,
                  'preview_filename': source_html.name, 'preview_sha256': hashlib.sha256(raw).hexdigest(),
                  'sample_count': len(points), 'gate_count': len(gates), 'closed_length_m': closed_length,
                  'accepted_length_m': stated_length,
                  'mean_target_speed_mps': sum(p['speed'] for p in points)/len(points),
                  'first_gate_width_m': gates[0]['width_m'], 'inherited_files': inherited,
                  'precision_note': 'Recovered rounded preview samples; not byte-identical original EZ JSON. Gate geolocation inverted from rounded preview XY.',
                  'gate_distance_note': 'Original preview gate s refers to the source line. Reprojected onto EZ segments; first gate is zero and lap wrap equals recovered closed length. Original values retained as source_s_m.',
                  'environment_note': 'Base environment dependencies copied unchanged; preview scenery retained separately, not promoted as new measured geography.'}
        blobs['recovery.json'] = _json_bytes(report)
        # Keep all the surviving environmental evidence without silently replacing authored assets.
        blobs['preview-data.json'] = _json_bytes(data)
        file_hashes = {name: hashlib.sha256(blob).hexdigest() for name, blob in sorted(blobs.items())}
        digest = hashlib.sha256()
        for name, blob in sorted(blobs.items()):
            digest.update(name.encode('utf-8') + b'\0' + blob + b'\0')
        manifest.update({'source_pack': source_id, 'recovery': 'recovery.json',
                         'certification': {'status': 'provisional', 'notes': 'OSM-derived circuit reconstruction and recovered preview; not surveyed or historically certified.'},
                         'file_hashes': file_hashes, 'content_hash': 'sha256:' + digest.hexdigest()})
        blobs['manifest.json'] = _json_bytes(manifest)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f'{source_html.name}: {exc}') from exc

    # Complete validation before creating the output. Exclusive files preserve partial runs for diagnosis.
    output_dir.mkdir(parents=True, exist_ok=False)
    for name, blob in blobs.items():
        with (output_dir / name).open('xb') as output:
            output.write(blob)
    return {**report, 'content_hash': manifest['content_hash']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_html', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--base-pack', type=Path)
    args = parser.parse_args()
    print(json.dumps(recover_preview(args.source_html, args.output_dir, base_pack=args.base_pack), indent=2))


if __name__ == '__main__':
    main()
