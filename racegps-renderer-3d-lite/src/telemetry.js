/**
 * RaceGPS Telemetry Engine
 * Handles GPS coordinate parsing, interpolation, speed, heading, and lateral G-force.
 */

class TelemetryEngine {
  constructor() {
    this.points = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.playbackRate = 2.0;
    this.listeners = [];
  }

  loadSyntheticTrack(trackName = 'monaco') {
    // Generate synthetic GPS telemetry along Monaco Grand Prix Circuit
    // Origin: 43.7374° N, 7.4211° E (Monaco Harbor / Grand Prix)
    const baseLat = 43.7374;
    const baseLng = 7.4211;
    const totalPoints = 300;
    this.points = [];

    for (let i = 0; i < totalPoints; i++) {
      const angle = (i / totalPoints) * Math.PI * 2;
      // Loop shape simulating track circuit with elevation variation
      const radiusLat = 0.003 * (1 + 0.3 * Math.sin(angle * 3));
      const radiusLng = 0.005 * (1 + 0.2 * Math.cos(angle * 2));

      const lat = baseLat + radiusLat * Math.sin(angle);
      const lng = baseLng + radiusLng * Math.cos(angle);
      const altitude = 15 + 12 * Math.sin(angle * 4); // elevation in meters
      const speedMph = 65 + 45 * Math.sin(angle * 5) + (Math.random() * 2 - 1);
      const lateralG = 0.8 * Math.cos(angle * 3);

      this.points.push({
        index: i,
        lat: lat,
        lng: lng,
        alt: altitude,
        speedMph: Math.max(20, Math.round(speedMph)),
        gForce: parseFloat(lateralG.toFixed(2)),
        timestamp: i * 200 // 5Hz sampling
      });
    }

    this.calculateHeadings();
    this.currentIndex = 0;
    return this.points;
  }

  calculateHeadings() {
    for (let i = 0; i < this.points.length; i++) {
      const nextIdx = (i + 1) % this.points.length;
      const p1 = this.points[i];
      const p2 = this.points[nextIdx];
      p1.heading = this.calculateBearing(p1.lat, p1.lng, p2.lat, p2.lng);
    }
  }

  calculateBearing(lat1, lon1, lat2, lon2) {
    const toRad = (deg) => (deg * Math.PI) / 180;
    const toDeg = (rad) => (rad * 180) / Math.PI;

    const dLon = toRad(lon2 - lon1);
    const y = Math.sin(dLon) * Math.cos(toRad(lat2));
    const x =
      Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
      Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLon);

    return (toDeg(Math.atan2(y, x)) + 360) % 360;
  }

  getCurrentPoint() {
    return this.points[this.currentIndex] || null;
  }

  nextFrame() {
    if (!this.isPlaying || this.points.length === 0) return null;
    this.currentIndex = (this.currentIndex + 1) % this.points.length;
    const point = this.getCurrentPoint();
    this.notify(point);
    return point;
  }

  subscribe(callback) {
    this.listeners.push(callback);
  }

  notify(point) {
    this.listeners.forEach((fn) => fn(point));
  }
}

window.TelemetryEngine = TelemetryEngine;
