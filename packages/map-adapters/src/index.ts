export interface MapPoint { lat: number; lon: number }

export interface MapAdapter {
  name: string;
  mount(container: HTMLElement): void;
  setCenter(point: MapPoint, zoom?: number): void;
  upsertPlayerMarker(playerId: string, point: MapPoint, label: string): void;
  removePlayerMarker(playerId: string): void;
  drawRoute(points: MapPoint[]): void;
  destroy(): void;
}

export class MockMapAdapter implements MapAdapter {
  name = 'mock-map';
  private container?: HTMLElement;
  private markers = new Map<string, HTMLElement>();

  mount(container: HTMLElement): void {
    this.container = container;
    container.innerHTML = '<div class="mock-map-grid"><div class="mock-map-title">raceGPS World Shell</div></div>';
  }

  setCenter(point: MapPoint): void {
    if (this.container) this.container.dataset.center = `${point.lat},${point.lon}`;
  }

  upsertPlayerMarker(playerId: string, point: MapPoint, label: string): void {
    if (!this.container) return;
    let el = this.markers.get(playerId);
    if (!el) {
      el = document.createElement('div');
      el.className = 'player-marker';
      this.container.appendChild(el);
      this.markers.set(playerId, el);
    }
    const x = 50 + ((point.lon * 1000) % 35);
    const y = 50 + ((point.lat * 1000) % 35);
    el.style.left = `${Math.max(8, Math.min(92, x))}%`;
    el.style.top = `${Math.max(8, Math.min(92, y))}%`;
    el.textContent = label.slice(0, 2).toUpperCase();
    el.title = `${label}: ${point.lat.toFixed(4)}, ${point.lon.toFixed(4)}`;
  }

  removePlayerMarker(playerId: string): void {
    this.markers.get(playerId)?.remove();
    this.markers.delete(playerId);
  }

  drawRoute(): void {}

  destroy(): void {
    this.container = undefined;
    this.markers.clear();
  }
}
