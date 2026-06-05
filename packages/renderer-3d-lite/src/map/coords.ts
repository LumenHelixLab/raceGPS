/**
 * World coordinate conversions.
 * Local: X=east, Y=up, Z=south (meters from origin).
 * Geo: lat/lon (WGS84).
 */

const METERS_PER_DEG_LAT = 111320;

export function metersPerDegLon(lat: number): number {
  return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180);
}

export class LocalCoords {
  originLat: number;
  originLon: number;
  cosOriginLat: number;

  constructor(originLat: number, originLon: number) {
    this.originLat = originLat;
    this.originLon = originLon;
    this.cosOriginLat = Math.cos((originLat * Math.PI) / 180);
  }

  toLocal(lat: number, lon: number, altitude = 0) {
    const dLat = lat - this.originLat;
    const dLon = lon - this.originLon;
    return {
      x: dLon * METERS_PER_DEG_LAT * this.cosOriginLat,
      y: altitude,
      z: -dLat * METERS_PER_DEG_LAT, // north is -Z
    };
  }

  toLatLon(x: number, z: number) {
    return {
      lat: this.originLat + (-z / METERS_PER_DEG_LAT),
      lon: this.originLon + (x / (METERS_PER_DEG_LAT * this.cosOriginLat)),
    };
  }
}
