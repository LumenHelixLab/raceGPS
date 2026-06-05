import maplibregl from 'maplibre-gl';
import { Protocol } from 'pmtiles';

let protocolRegistered = false;

export function registerPMTilesProtocol(): void {
  if (protocolRegistered) return;
  const protocol = new Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);
  protocolRegistered = true;
}
