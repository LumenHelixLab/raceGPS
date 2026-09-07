"""Behavioral fixtures for route continuity, direction and immutable generation."""
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/universal-city-compiler'))
sys.path.insert(0, str(ROOT / 'scripts'))
from road_network import build_road_graph
from route_engine import generate_routes, directed_graph
from citypack_audit import audit, digest
from compile_snapshot import compile_snapshot


def osm(tmp_path, ways, nodes=None):
    nodes = nodes or [('1', 41, -81), ('2', 41.01, -81), ('3', 41.01, -81.01), ('4', 41, -81.01)]
    text = '<osm>' + ''.join(f'<node id="{n}" lat="{lat}" lon="{lon}"/>' for n, lat, lon in nodes)
    for rid, ids, tags in ways:
        text += f'<way id="{rid}">' + ''.join(f'<nd ref="{n}"/>' for n in ids)
        text += '<tag k="highway" v="residential"/>' + ''.join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items()) + '</way>'
    path = tmp_path / 'source.osm'
    path.write_text(text + '</osm>')
    return path


def test_close_parallel_roads_do_not_connect(tmp_path):
    path = osm(tmp_path, [('a', ['1', '2'], {}), ('b', ['3', '4'], {})],
               [('1',41,-81),('2',41.002,-81),('3',41.0021,-81),('4',41.004,-81)])
    graph = build_road_graph(path)
    assert generate_routes(graph, 'test', mode='cruise_sprint', count=1) == []


def test_open_path_never_masquerades_as_circuit(tmp_path):
    graph = build_road_graph(osm(tmp_path, [('a', ['1', '2', '3', '4'], {})]))
    assert generate_routes(graph, 'test', mode='circuit', count=1) == []


def test_true_circuit_closed_and_permutation_stable(tmp_path):
    graph = build_road_graph(osm(tmp_path, [('a', ['1','2'], {}), ('b', ['2','3'], {}),
                                             ('c', ['3','4'], {}), ('d', ['4','1'], {})]))
    routes = generate_routes(graph, 'test', mode='circuit', count=1)
    assert routes and routes[0]['start'] == routes[0]['finish']
    assert len(routes[0]['segments']) == 4
    graph['roads'].reverse()
    graph['intersections'].reverse()
    assert generate_routes(graph, 'test', mode='circuit', count=1) == routes


def test_reverse_oneway_and_roundabout(tmp_path):
    graph = build_road_graph(osm(tmp_path, [('a', ['1','2'], {'oneway':'-1'}),
                                              ('b',['3','4'],{'junction':'roundabout'})]))
    adjacency, _ = directed_graph(graph)
    assert graph['roads'][0]['node_ids'] == ['2', '1']
    assert all(e['direction'] == 1 for edges in adjacency.values() for _, e in edges)


def test_shared_bridge_endpoint_connects_without_snapping(tmp_path):
    graph = build_road_graph(osm(tmp_path, [('a',['1','2'], {}), ('b',['2','3'], {'bridge':'yes'})]))
    assert graph['intersections'][0]['layer_transition']
    routes = generate_routes(graph, 'test', mode='time_trial', count=1)
    assert routes and {e['road_id'] for e in routes[0]['segments']} == {'a','b'}


def test_incomplete_source_rejected(tmp_path):
    path = osm(tmp_path, [('a', ['1','missing','2'], {})])
    with pytest.raises(ValueError, match='missing nodes'):
        build_road_graph(path)
    path.write_text('<osm><node id="1"/></osm>')
    with pytest.raises(ValueError, match='no coordinates'):
        build_road_graph(path)


def test_offline_rebuild_is_identical_and_not_race_ready(tmp_path):
    source = osm(tmp_path, [('a',['1','2'], {})])
    record = tmp_path / 'source.json'
    record.write_text(json.dumps({'sha256':digest(source), 'url':'fixture://synthetic',
         'retrieved_at':'fixture', 'attribution':'Synthetic test data', 'license_url':'fixture://license'}))
    a,b = tmp_path/'a',tmp_path/'b'
    first = compile_snapshot(source,record,a,'test',(41,-81))
    assert compile_snapshot(source,record,b,'test',(41,-81)) == first
    assert (a/'test_semantic_manifest.json').read_bytes() == (b/'test_semantic_manifest.json').read_bytes()
    report = audit(a)
    assert report['status'] == 'failed' and 'No playable routes' in report['errors']
    assert report['road_identity_difference']['graph_only_count'] == 0
    with pytest.raises(ValueError, match='fresh directory'):
        compile_snapshot(source,record,a,'test',(41,-81))
    source.write_text(source.read_text()+'\n')
    with pytest.raises(ValueError, match='Source hash'):
        compile_snapshot(source,record,tmp_path/'c','test',(41,-81))


def test_manifest_path_escape_rejected(tmp_path):
    (tmp_path/'test_semantic_manifest.json').write_text(json.dumps({'files':{'routes':'../secret.json'}}))
    assert 'escapes citypack' in audit(tmp_path)['errors'][0]


def test_audit_rejects_route_jump_and_altered_points(tmp_path):
    source = osm(tmp_path, [('a',['1','2','3','4','1'], {})])
    record = tmp_path/'source.json'
    record.write_text(json.dumps({'sha256':digest(source), 'url':'fixture://synthetic',
         'retrieved_at':'fixture', 'attribution':'Synthetic', 'license_url':'fixture://license'}))
    output = tmp_path/'pack'
    compile_snapshot(source,record,output,'test',(41,-81))
    graph = json.loads((output/'test_road_graph.json').read_text())
    routes = generate_routes(graph, 'test', mode='circuit', count=1)
    manifest_path = output/'test_semantic_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest.pop('sha256')
    manifest.pop('release_ready')
    manifest_path.write_text(json.dumps(manifest))
    (output/'test_routes.json').write_text(json.dumps(routes))
    (output/'test_spawn_points.json').write_text(json.dumps([routes[0]['start']]))
    assert audit(output)['status'] == 'passed'
    routes[0]['points'][0] = {'lat':0,'lon':0}
    (output/'test_routes.json').write_text(json.dumps(routes))
    assert any('points differ' in e for e in audit(output)['errors'])
    routes[0]['segments'][0]['direction'] = 8
    (output/'test_routes.json').write_text(json.dumps(routes))
    assert any('illegal or disconnected' in e for e in audit(output)['errors'])
