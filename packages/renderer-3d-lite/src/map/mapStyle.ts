import type { StyleSpecification } from 'maplibre-gl';

/**
 * Dark neon vector basemap for raceGPS.
 * Matches the spec: dark, clean, neon, fast, readable.
 */
export function createRaceMapStyle(): StyleSpecification {
  return {
    version: 8,
    sources: {
      openmaptiles: {
        type: 'vector',
        url: 'https://tiles.openfreemap.org/planet',
      },
    },
    glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
    layers: [
      // Deep space background
      { id: 'background', type: 'background', paint: { 'background-color': '#0a0a12' } },

      // Water
      { id: 'water', type: 'fill', source: 'openmaptiles', 'source-layer': 'water',
        paint: { 'fill-color': '#0d1b2a', 'fill-opacity': 0.9 } },

      // Land
      { id: 'landcover', type: 'fill', source: 'openmaptiles', 'source-layer': 'landcover',
        paint: { 'fill-color': '#111118' } },

      // Minor roads (dim)
      { id: 'road-minor', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'service', 'path', 'track']],
        paint: { 'line-color': '#1a1a24', 'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 2] } },

      // Tertiary roads
      { id: 'road-tertiary', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'tertiary']],
        paint: { 'line-color': '#22222e', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1, 16, 3] } },

      // Secondary roads
      { id: 'road-secondary', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'secondary']],
        paint: { 'line-color': '#2a2a38', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1, 16, 4] } },

      // Primary roads (warm yellow for visibility)
      { id: 'road-primary', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'primary']],
        paint: { 'line-color': '#3d3525', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.5, 16, 5] } },

      // Motorways (neon orange)
      { id: 'road-motorway', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'motorway', 'trunk']],
        paint: { 'line-color': '#4a3520', 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1, 16, 6] } },

      // Road casing (subtle outline)
      { id: 'road-casing', type: 'line', source: 'openmaptiles', 'source-layer': 'transportation',
        filter: ['all', ['==', '$type', 'LineString'], ['in', 'class', 'primary', 'secondary', 'tertiary']],
        paint: { 'line-color': '#0a0a12', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 2, 16, 7], 'line-gap-width': ['interpolate', ['linear'], ['zoom'], 12, 1, 16, 4] } },

      // Buildings (dark extruded)
      { id: 'buildings', type: 'fill-extrusion', source: 'openmaptiles', 'source-layer': 'building',
        minzoom: 14,
        paint: {
          'fill-extrusion-color': '#1c1c28',
          'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 14, 0, 16, ['get', 'render_height']],
          'fill-extrusion-base': 0,
          'fill-extrusion-opacity': 0.85,
          'fill-extrusion-vertical-gradient': true,
        } },

      // Road labels (minimal, white)
      { id: 'road-label', type: 'symbol', source: 'openmaptiles', 'source-layer': 'transportation_name',
        minzoom: 14,
        layout: { 'text-field': '{name}', 'text-size': 10, 'text-font': ['Noto Sans Regular'] },
        paint: { 'text-color': '#8888aa', 'text-halo-color': '#0a0a12', 'text-halo-width': 1.5 } },

      // Place labels
      { id: 'place-label', type: 'symbol', source: 'openmaptiles', 'source-layer': 'place',
        minzoom: 10,
        layout: { 'text-field': '{name}', 'text-size': 13, 'text-font': ['Noto Sans Bold'] },
        paint: { 'text-color': '#aabbee', 'text-halo-color': '#0a0a12', 'text-halo-width': 2 } },
    ],
  } as StyleSpecification;
}
