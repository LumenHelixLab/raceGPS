import type { GameMode } from '../renderer.js';

export interface LayerVisibility {
  roads: boolean;
  buildings: boolean;
  routeRibbon: boolean;
  checkpoints: boolean;
  pickups: boolean;
  playerMarkers: boolean;
  labels: boolean;
  heatZones: boolean;
}

const MODE_LAYERS: Record<GameMode, LayerVisibility> = {
  cruise: {
    roads: true,
    buildings: true,
    routeRibbon: false,
    checkpoints: false,
    pickups: false,
    playerMarkers: true,
    labels: true,
    heatZones: false,
  },
  race: {
    roads: true,
    buildings: true,
    routeRibbon: true,
    checkpoints: true,
    pickups: false,
    playerMarkers: true,
    labels: false,
    heatZones: false,
  },
  challenge: {
    roads: true,
    buildings: true,
    routeRibbon: false,
    checkpoints: false,
    pickups: true,
    playerMarkers: true,
    labels: false,
    heatZones: false,
  },
  hotpursuit: {
    roads: true,
    buildings: true,
    routeRibbon: false,
    checkpoints: false,
    pickups: false,
    playerMarkers: true,
    labels: false,
    heatZones: true,
  },
  explore: {
    roads: true,
    buildings: true,
    routeRibbon: false,
    checkpoints: false,
    pickups: false,
    playerMarkers: false,
    labels: true,
    heatZones: false,
  },
};

export function getLayerVisibility(mode: GameMode): LayerVisibility {
  return MODE_LAYERS[mode] ?? MODE_LAYERS.cruise;
}
