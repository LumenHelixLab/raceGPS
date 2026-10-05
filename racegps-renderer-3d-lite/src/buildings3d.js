/**
 * RaceGPS 3D Procedural Building Generator
 * Styles OpenStreetMap building extrusions in Synthwave / Midnight Run Arcade theme.
 */

class ProceduralBuildingGenerator {
  constructor(map) {
    this.map = map;
  }

  enableVector3DBuildings() {
    if (!this.map.getSource('openfreemap-vector')) {
      this.map.addSource('openfreemap-vector', {
        type: 'vector',
        url: 'https://tiles.openfreemap.org/planet'
      });
    }

    if (!this.map.getLayer('3d-buildings')) {
      this.map.addLayer({
        id: '3d-buildings',
        type: 'fill-extrusion',
        source: 'openfreemap-vector',
        'source-layer': 'building',
        filter: ['!=', ['get', 'hide_3d'], true],
        paint: {
          'fill-extrusion-color': [
            'interpolate',
            ['linear'],
            ['get', 'render_height'],
            0, '#090d16',
            20, '#0f172a',
            50, '#1e1b4b',
            100, '#31103f'
          ],
          'fill-extrusion-height': [
            'interpolate',
            ['linear'],
            ['zoom'],
            13, 0,
            14.5, ['get', 'render_height']
          ],
          'fill-extrusion-base': [
            'interpolate',
            ['linear'],
            ['zoom'],
            13, 0,
            14.5, ['get', 'render_min_height']
          ],
          'fill-extrusion-opacity': 0.9
        }
      });
    }
  }
}

window.ProceduralBuildingGenerator = ProceduralBuildingGenerator;
